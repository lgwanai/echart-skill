"""Unified SQL runner for echart-skill.

Use this script instead of ad-hoc ``python <<EOF`` snippets for database
queries. It supports local DuckDB and configured external SQL profiles, applies
the privacy/audit pipeline, and writes stable table/json/csv outputs.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database import _infer_table_name, get_repository
from scripts.audit_report import log_command
from scripts.config_manager import get_config
from scripts.db_cli import _execute_with_audit, get_profile
from pydantic import SecretStr

from scripts.db_config import ConnectionProfile
from scripts.db_connector import SQLConnector, create_connector
from scripts.lineage_manager import LineageRecord, hash_query, record_lineage
from scripts.metrics_manager import render_effective_metrics
from scripts.privacy_guard import PrivacyGuard


def _read_sql(args: argparse.Namespace) -> str:
    if args.sql_option:
        return args.sql_option.strip()
    if args.file:
        return Path(args.file).read_text(encoding="utf-8").strip()
    if args.stdin:
        return sys.stdin.read().strip()
    if args.sql:
        return args.sql.strip()
    raise SystemExit("Error: provide SQL with --sql, as an argument, --file, or --stdin")


def _privacy_guard(read_only: bool) -> PrivacyGuard:
    cfg = get_config()
    return PrivacyGuard(
        enabled=True,
        read_only=read_only,
        audit_enabled=cfg.privacy.audit_enabled,
        mask_pii=cfg.privacy.mask_pii,
        audit_log_path=cfg.privacy.audit_log_path,
    )


def _execute_duckdb(sql: str, db_path: str, allow_write: bool) -> list[dict[str, Any]]:
    guard = _privacy_guard(read_only=not allow_write)
    guard.enforce_read_only(sql)
    repo = get_repository(db_path)
    rows = repo.execute_query_raw(sql)
    columns = list(rows[0].keys()) if rows else []
    return guard.guard_query(sql, _infer_table_name(sql), columns, rows)


def _profile_from_dsn(dsn: str, db_type: str) -> ConnectionProfile:
    if not db_type:
        lower = dsn.lower()
        if lower.startswith(("postgresql://", "postgres://", "postgresql+psycopg2://")):
            db_type = "postgresql"
        elif lower.startswith(("mysql://", "mysql+pymysql://")):
            db_type = "mysql"
        else:
            raise SystemExit("Error: --type is required when --dsn-env scheme is not PostgreSQL/MySQL")
    if db_type not in {"postgresql", "mysql"}:
        raise SystemExit("Error: --dsn-env only supports SQL database types: postgresql, mysql")
    return ConnectionProfile(type=db_type, connection_string=dsn)


def _profile_from_connection_args(args: argparse.Namespace) -> ConnectionProfile:
    if not args.type:
        raise SystemExit("Error: --type is required with direct connection parameters")
    if not args.host:
        raise SystemExit("Error: --host is required with direct connection parameters")
    if not args.database:
        raise SystemExit("Error: --database is required with direct connection parameters")

    password = None
    if args.password_env:
        raw_password = os.environ.get(args.password_env, "")
        if not raw_password:
            raise SystemExit(f"Error: environment variable {args.password_env!r} is empty or not set")
        password = SecretStr(raw_password)

    return ConnectionProfile(
        type=args.type,
        host=args.host,
        port=args.port,
        database=args.database,
        username=args.username,
        password=password,
        db_schema=args.schema,
        timeout=args.timeout,
    )


def _execute_external_profile(sql: str, profile_name: str, config_path: str, allow_write: bool) -> list[dict[str, Any]]:
    guard = _privacy_guard(read_only=not allow_write)
    guard.enforce_read_only(sql)
    profile = get_profile(config_path or None, profile_name)
    connector = create_connector(profile)
    try:
        if not isinstance(connector, SQLConnector):
            raise SystemExit("Error: sql_runner supports SQL profiles only; use db_cli.py for MongoDB.")
        return _execute_with_audit(connector=connector, query=sql, profile_name=profile_name)
    finally:
        connector.close()


def _execute_external_dsn(sql: str, dsn_env: str, db_type: str, allow_write: bool) -> list[dict[str, Any]]:
    dsn = os.environ.get(dsn_env, "")
    if not dsn:
        raise SystemExit(f"Error: environment variable {dsn_env!r} is empty or not set")
    guard = _privacy_guard(read_only=not allow_write)
    guard.enforce_read_only(sql)
    profile = _profile_from_dsn(dsn, db_type)
    connector = SQLConnector(profile)
    try:
        return _execute_with_audit(connector=connector, query=sql, profile_name=f"env:{dsn_env}")
    finally:
        connector.close()


def _execute_external_connection_args(sql: str, args: argparse.Namespace) -> list[dict[str, Any]]:
    guard = _privacy_guard(read_only=not args.allow_write)
    guard.enforce_read_only(sql)
    profile = _profile_from_connection_args(args)
    connector = SQLConnector(profile)
    profile_label = f"args:{args.type}:{args.host}/{args.database}"
    try:
        return _execute_with_audit(connector=connector, query=sql, profile_name=profile_label)
    finally:
        connector.close()


def _format_rows(rows: list[dict[str, Any]], output_format: str, max_rows: int | None) -> str:
    visible_rows = rows[:max_rows] if max_rows and max_rows > 0 else rows
    if output_format == "json":
        return json.dumps(visible_rows, ensure_ascii=False, indent=2, default=str)
    if output_format == "csv":
        if not visible_rows:
            return ""
        handle = io.StringIO()
        writer = csv.DictWriter(handle, fieldnames=list(visible_rows[0].keys()))
        writer.writeheader()
        writer.writerows(visible_rows)
        return handle.getvalue()
    if not visible_rows:
        return "No results."
    return pd.DataFrame(visible_rows).to_markdown(index=False)


def _write_output(text: str, output_path: str) -> None:
    if not output_path:
        print(text)
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"Wrote result: {path}")


def _sidecar_path(output_path: str) -> Path:
    return Path(str(Path(output_path)) + ".meta.json")


def _write_enterprise_metadata(
    *,
    output_path: str,
    sql: str,
    rows: list[dict[str, Any]],
    source_label: str,
    generated_by: str,
) -> None:
    if not output_path:
        return
    artifact = Path(output_path).resolve()
    columns = list(rows[0].keys()) if rows else []
    table = _infer_table_name(sql)
    q_hash = hash_query(sql)
    metrics = render_effective_metrics(os.getcwd())
    metadata = {
        "artifact_path": str(artifact),
        "artifact_type": "query_result",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "generated_by": generated_by,
        "source": source_label,
        "source_tables": [table] if table else [],
        "columns": columns,
        "row_count": len(rows),
        "query_hash": q_hash,
        "effective_metrics": metrics,
        "lineage_recorded": True,
        "quality_requirement": "Enterprise BI query outputs require scope, lineage, auditability, row/column metadata, and no raw DB connection code.",
    }
    sidecar = _sidecar_path(output_path)
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    sidecar.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    record_lineage(LineageRecord(
        artifact_path=str(artifact),
        artifact_type="query",
        source_tables=[table] if table else [],
        columns=columns,
        query_hashes=[q_hash],
        metric_scopes=["effective_metrics"],
        generated_by=generated_by,
        notes=f"source={source_label}; rows={len(rows)}; metadata={sidecar}",
    ))
    print(f"Wrote metadata: {sidecar}")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified audited SQL runner")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--db", default="workspace.duckdb", help="DuckDB path; default workspace.duckdb")
    source.add_argument("--profile", help="External SQL connection profile from /dbconn")
    source.add_argument("--dsn-env", help="Environment variable containing a SQLAlchemy DSN")
    parser.add_argument("--config", default="", help="Optional db_connections.txt path for --profile")
    parser.add_argument("--type", choices=["postgresql", "mysql"], default="", help="Database type for --dsn-env or direct connection parameters")
    parser.add_argument("--host", help="Direct SQL database host; use instead of ad-hoc Python connections")
    parser.add_argument("--port", type=int, help="Direct SQL database port")
    parser.add_argument("--database", help="Direct SQL database name")
    parser.add_argument("--username", "--user", dest="username", help="Direct SQL database username")
    parser.add_argument("--password-env", help="Environment variable containing the direct SQL database password")
    parser.add_argument("--schema", help="Optional schema name for direct PostgreSQL connections")
    parser.add_argument("--timeout", type=float, default=30.0, help="Direct SQL connection timeout in seconds")
    parser.add_argument("--sql", dest="sql_option", help="SQL string to execute directly; preferred for agent-generated SQL")
    parser.add_argument("--file", "-f", help="Read SQL from a task/reviewable .sql file. Agent may write SQL files, but execution must stay in this runner.")
    parser.add_argument("--stdin", action="store_true", help="Read SQL from stdin")
    parser.add_argument("--output", "-o", choices=["table", "json", "csv"], default="table")
    parser.add_argument("--out", help="Write formatted output to file")
    parser.add_argument("--max-rows", type=int, help="Max rows to render; default stdout=200, --out=all")
    parser.add_argument("--allow-write", action="store_true", help="Allow DDL/DML. Default is read-only.")
    parser.add_argument("sql", nargs="?", help="SQL string")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = create_parser()
    args = parser.parse_args(argv)
    sql = _read_sql(args)
    log_command("sql_runner", status="started", note=_infer_table_name(sql))
    try:
        if args.profile:
            rows = _execute_external_profile(sql, args.profile, args.config, args.allow_write)
            source_label = f"profile:{args.profile}"
        elif args.dsn_env:
            rows = _execute_external_dsn(sql, args.dsn_env, args.type, args.allow_write)
            source_label = f"dsn-env:{args.dsn_env}"
        elif args.host or args.database or args.username or args.password_env:
            rows = _execute_external_connection_args(sql, args)
            source_label = f"args:{args.type}:{args.host}/{args.database}"
        else:
            rows = _execute_duckdb(sql, args.db, args.allow_write)
            source_label = f"duckdb:{args.db}"
        max_rows = args.max_rows if args.max_rows is not None else (0 if args.out else 200)
        text = _format_rows(rows, args.output, max_rows)
        _write_output(text, args.out or "")
        _write_enterprise_metadata(
            output_path=args.out or "",
            sql=sql,
            rows=rows,
            source_label=source_label,
            generated_by="sql_runner",
        )
        if max_rows > 0 and len(rows) > max_rows and not args.out:
            print(f"\nShowing {max_rows} of {len(rows)} rows. Use --max-rows 0 or --out for full output.")
        log_command("sql_runner", status="completed", note=f"rows={len(rows)}")
    except Exception as exc:
        log_command("sql_runner", status="failed", note=str(exc)[:200])
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
