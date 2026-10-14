#!/usr/bin/env python3
"""Maintain a project-local index of known databases and data files.

The index stores discovery metadata only: profile names, database/schema names,
table/file structure, row counts, inferred column roles, fingerprints, and usage
history. It never stores passwords, hosts, connection strings, or sampled values.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))


CONTEXT_DIRNAME = ".echart-skill"
CONTEXT_FILENAME = "data_sources.json"
SUPPORTED_FILES = {".csv", ".xlsx", ".xls", ".et", ".numbers", ".json", ".jsonl", ".ndjson", ".parquet"}
NUMERIC_TYPE_TOKENS = ("int", "decimal", "numeric", "double", "float", "real", "number")
TIME_NAME_TOKENS = ("date", "time", "day", "week", "month", "quarter", "year", "日期", "时间", "年月", "月份", "年度")


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def discover_project_root(start: str | os.PathLike[str] | None = None) -> Path:
    current = Path(start or os.getcwd()).expanduser().resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / CONTEXT_DIRNAME).exists() or (candidate / ".git").exists():
            return candidate
    return current


def get_context_path(project_root: str | os.PathLike[str] | None = None) -> Path:
    return discover_project_root(project_root) / CONTEXT_DIRNAME / CONTEXT_FILENAME


def empty_context(project_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "project_root": str(project_root),
        "updated_at": _now(),
        "privacy": {
            "stores_credentials": False,
            "stores_sample_values": False,
            "description": "Structure and source-location metadata only",
        },
        "sources": [],
    }


def load_context(project_root: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    root = discover_project_root(project_root)
    path = get_context_path(root)
    if not path.exists():
        return empty_context(root)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Invalid project data context: {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("sources"), list):
        raise ValueError(f"Unsupported project data context format: {path}")
    return data


def save_context(context: dict[str, Any], project_root: str | os.PathLike[str] | None = None) -> Path:
    root = discover_project_root(project_root or context.get("project_root"))
    path = get_context_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    context["version"] = 1
    context["project_root"] = str(root)
    context["updated_at"] = _now()
    context.setdefault("privacy", empty_context(root)["privacy"])
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)
    return path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _infer_role(name: str, data_type: str = "") -> str:
    lower = name.lower()
    dtype = data_type.lower()
    if lower == "id" or lower.endswith("_id") or lower.endswith("编号"):
        return "identifier"
    if any(token in lower for token in TIME_NAME_TOKENS) or any(token in dtype for token in ("date", "time")):
        return "time"
    if any(token in dtype for token in NUMERIC_TYPE_TOKENS):
        return "measure"
    return "dimension"


def _safe_description(value: Any) -> str:
    text = str(value or "").strip()
    if not text or re.match(r"^(?:例如|示例|样例)\s*[:：]", text):
        return ""
    sensitive_patterns = (
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        r"(?<!\d)1[3-9]\d{9}(?!\d)",
        r"(?<!\d)\d{15,18}[0-9Xx](?!\d)",
    )
    if any(re.search(pattern, text) for pattern in sensitive_patterns):
        return ""
    return text[:240]


def _column_summary(
    name: Any,
    data_type: Any,
    nullable: bool = True,
    description: str = "",
) -> dict[str, Any]:
    clean_name = str(name)
    clean_type = str(data_type)
    result = {
        "name": clean_name,
        "type": clean_type,
        "nullable": bool(nullable),
        "role": _infer_role(clean_name, clean_type),
    }
    safe_description = _safe_description(description)
    if safe_description:
        result["description"] = safe_description
    return result


def _asset_summary(
    name: str,
    columns: Iterable[dict[str, Any]],
    *,
    row_count: int | None = None,
    namespace: str = "",
    description: str = "",
) -> dict[str, Any]:
    clean_columns = list(columns)
    roles: dict[str, list[str]] = {"time": [], "measure": [], "dimension": [], "identifier": []}
    for column in clean_columns:
        roles.setdefault(str(column.get("role", "unknown")), []).append(str(column.get("name", "")))
    result: dict[str, Any] = {
        "name": name,
        "column_count": len(clean_columns),
        "columns": clean_columns,
        "content_summary": {
            "time_fields": roles.get("time", []),
            "measure_fields": roles.get("measure", []),
            "dimension_fields": roles.get("dimension", []),
            "identifier_fields": roles.get("identifier", []),
        },
    }
    if namespace:
        result["namespace"] = namespace
    safe_description = _safe_description(description)
    if safe_description:
        result["description"] = safe_description
    if row_count is not None and row_count >= 0:
        result["row_count"] = int(row_count)
    return result


def _upsert_source(context: dict[str, Any], source: dict[str, Any]) -> None:
    existing = next((item for item in context["sources"] if item.get("id") == source["id"]), None)
    if existing:
        for key in ("aliases", "notes", "use_count", "last_used_at", "last_query"):
            if key in existing and key not in source:
                source[key] = existing[key]
    context["sources"] = [item for item in context["sources"] if item.get("id") != source["id"]]
    context["sources"].append(source)
    context["sources"].sort(key=lambda item: str(item.get("id", "")))


def _safe_profile_metadata(profile: Any) -> dict[str, Any]:
    return {
        "db_type": str(getattr(profile, "type", "unknown")),
        "database": str(getattr(profile, "database", "") or ""),
        "db_schema": str(getattr(profile, "db_schema", "") or ""),
    }


def _schema_annotations(root: Path) -> dict[str, Any]:
    try:
        from scripts.schema_manager import get_effective_schemas

        return get_effective_schemas(str(root))
    except (OSError, ValueError):
        return {}


def refresh_database_source(
    profile_name: str,
    *,
    project_root: str | os.PathLike[str] | None = None,
    max_assets: int = 200,
    include_row_counts: bool = True,
) -> tuple[dict[str, Any], Path]:
    """Connect to a configured profile and persist a credential-free schema summary."""
    from scripts.db_config import load_effective_config
    from scripts.db_connector import MongoDBConnector, SQLConnector, create_connector
    from scripts.db_schema import (
        describe_table,
        discover_tables,
        get_table_row_count,
        infer_mongo_schema,
        list_mongo_collections,
    )

    root = discover_project_root(project_root)
    config = load_effective_config(str(root))
    if profile_name not in config.connections:
        raise KeyError(f"Connection profile not found: {profile_name}")
    profile = config.connections[profile_name]
    connector = create_connector(profile)
    assets: list[dict[str, Any]] = []
    discovered_count = 0
    annotations = _schema_annotations(root)
    try:
        connector.connect()
        if isinstance(connector, SQLConnector):
            namespace = profile.db_schema or ""
            names = discover_tables(connector, namespace or None)
            discovered_count = len(names)
            for name in names[:max_assets]:
                raw_columns = describe_table(connector, name, namespace or None)
                annotation = annotations.get(name)
                annotated_columns = {
                    column.name.lower(): column for column in getattr(annotation, "columns", [])
                }
                columns = [
                    _column_summary(
                        col.get("name", ""),
                        col.get("type", ""),
                        col.get("nullable", True),
                        getattr(annotated_columns.get(str(col.get("name", "")).lower()), "description", ""),
                    )
                    for col in raw_columns
                ]
                row_count = get_table_row_count(connector, name, namespace or None) if include_row_counts else None
                assets.append(_asset_summary(
                    name,
                    columns,
                    row_count=row_count,
                    namespace=namespace,
                    description=getattr(annotation, "description", ""),
                ))
        elif isinstance(connector, MongoDBConnector):
            names = list_mongo_collections(connector, profile.database or None)
            discovered_count = len(names)
            for name in names[:max_assets]:
                inferred = infer_mongo_schema(connector, name, sample_size=100)
                columns = [_column_summary(field, field_type) for field, field_type in sorted(inferred.items())]
                assets.append(_asset_summary(name, columns, namespace=profile.database or ""))
        else:
            raise ValueError(f"Unsupported connector for discovery: {type(connector).__name__}")
    finally:
        connector.close()

    context = load_context(root)
    source = {
        "id": f"database:{profile_name}",
        "kind": "database",
        "profile": profile_name,
        **_safe_profile_metadata(profile),
        "access": {"kind": "profile", "profile": profile_name},
        "status": "active",
        "discovered_at": _now(),
        "asset_count": discovered_count,
        "indexed_asset_count": len(assets),
        "truncated": discovered_count > len(assets),
        "assets": assets,
    }
    _upsert_source(context, source)
    return source, save_context(context, root)


def _relative_or_absolute(path: Path, root: Path) -> tuple[str, str]:
    try:
        return str(path.relative_to(root)), "project"
    except ValueError:
        return str(path), "external"


def _pandas_assets(path: Path, sample_rows: int) -> list[dict[str, Any]]:
    import pandas as pd

    suffix = path.suffix.lower()
    frames: list[tuple[str, Any, int | None]] = []
    if suffix == ".csv":
        frame = pd.read_csv(path, nrows=sample_rows)
        frames.append((path.stem, frame, None))
    elif suffix in {".xlsx", ".xls", ".et"}:
        workbook = pd.ExcelFile(path)
        for sheet in workbook.sheet_names:
            frame = pd.read_excel(path, sheet_name=sheet, nrows=sample_rows)
            frames.append((str(sheet), frame, None))
    elif suffix in {".jsonl", ".ndjson"}:
        frame = pd.read_json(path, lines=True, nrows=sample_rows)
        frames.append((path.stem, frame, None))
    elif suffix == ".json":
        if path.stat().st_size > 25 * 1024 * 1024:
            raise ValueError("JSON files over 25MB must be imported before registration")
        frame = pd.read_json(path)
        frames.append((path.stem, frame.head(sample_rows), len(frame)))
    elif suffix == ".parquet":
        try:
            import pyarrow.parquet as pq

            parquet = pq.ParquetFile(path)
            schema = parquet.schema_arrow
            columns = [_column_summary(field.name, field.type) for field in schema]
            return [_asset_summary(path.stem, columns, row_count=parquet.metadata.num_rows)]
        except ImportError:
            frame = pd.read_parquet(path).head(sample_rows)
            frames.append((path.stem, frame, None))
    else:
        raise ValueError(f"Direct structure discovery is not supported for {suffix}; import it first")

    assets: list[dict[str, Any]] = []
    for name, frame, row_count in frames:
        columns = [_column_summary(column, dtype) for column, dtype in frame.dtypes.items()]
        assets.append(_asset_summary(name, columns, row_count=row_count))
    return assets


def _duckdb_assets(db_path: Path, table_names: Iterable[str]) -> list[dict[str, Any]]:
    import duckdb

    assets: list[dict[str, Any]] = []
    connection = duckdb.connect(str(db_path), read_only=True)
    try:
        for table_name in table_names:
            escaped = str(table_name).replace('"', '""')
            rows = connection.execute(f'DESCRIBE "{escaped}"').fetchall()
            columns = [_column_summary(row[0], row[1], str(row[2]).upper() != "NO") for row in rows]
            row_count = connection.execute(f'SELECT COUNT(*) FROM "{escaped}"').fetchone()[0]
            assets.append(_asset_summary(str(table_name), columns, row_count=row_count))
    finally:
        connection.close()
    return assets


def register_file_source(
    file_path: str | os.PathLike[str],
    *,
    project_root: str | os.PathLike[str] | None = None,
    duckdb_path: str | os.PathLike[str] | None = None,
    table_names: Iterable[str] = (),
    sample_rows: int = 2000,
) -> tuple[dict[str, Any], Path]:
    root = discover_project_root(project_root)
    path = Path(file_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.suffix.lower() not in SUPPORTED_FILES:
        raise ValueError(f"Unsupported data file: {path.suffix}")
    relative_path, location_scope = _relative_or_absolute(path, root)
    materialized_tables = list(table_names)
    access: dict[str, Any] = {"kind": "file", "path": relative_path}
    if duckdb_path and materialized_tables:
        db_path = Path(duckdb_path).expanduser().resolve()
        db_ref, _ = _relative_or_absolute(db_path, root)
        assets = _duckdb_assets(db_path, materialized_tables)
        access = {"kind": "duckdb", "db_path": db_ref, "tables": materialized_tables}
    else:
        assets = _pandas_assets(path, sample_rows)

    stat = path.stat()
    context = load_context(root)
    source = {
        "id": f"file:{relative_path}",
        "kind": "file",
        "path": relative_path,
        "location_scope": location_scope,
        "format": path.suffix.lower().lstrip("."),
        "size_bytes": stat.st_size,
        "modified_ns": stat.st_mtime_ns,
        "sha256": _sha256(path),
        "status": "active",
        "discovered_at": _now(),
        "last_used_at": _now(),
        "use_count": 1,
        "access": access,
        "assets": assets,
    }
    _upsert_source(context, source)
    return source, save_context(context, root)


def _configured_profile_sources(root: Path) -> list[dict[str, Any]]:
    try:
        from scripts.db_config import load_effective_config

        # Resolver stdout is a machine-readable JSON contract; config logging
        # must not be mixed into it.
        with contextlib.redirect_stdout(io.StringIO()):
            config = load_effective_config(str(root))
    except (FileNotFoundError, ValueError):
        return []
    return [
        {
            "id": f"database:{name}",
            "kind": "database",
            "profile": name,
            **_safe_profile_metadata(profile),
            "status": "needs_refresh",
            "assets": [],
        }
        for name, profile in config.connections.items()
    ]


def _source_status(source: dict[str, Any], root: Path) -> str:
    if source.get("kind") != "file":
        return str(source.get("status", "active"))
    path = Path(str(source.get("path", "")))
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        return "missing"
    stat = path.stat()
    if stat.st_size != source.get("size_bytes") or stat.st_mtime_ns != source.get("modified_ns"):
        return "stale"
    return "active"


def _normalize(text: Any) -> str:
    return re.sub(r"[\W_]+", "", str(text).lower(), flags=re.UNICODE)


def _semantic_terms(query: str) -> set[str]:
    stop = {"分析", "数据", "报表", "报告", "看板", "趋势", "情况", "进行", "一下", "the", "data", "report", "analysis"}
    terms = {
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_]+", query)
        if len(token) >= 2 and token.lower() not in stop
    }
    for sequence in re.findall(r"[\u4e00-\u9fff]+", query):
        for width in range(2, min(4, len(sequence)) + 1):
            for start in range(0, len(sequence) - width + 1):
                term = sequence[start:start + width]
                if term not in stop:
                    terms.add(term)
    return terms


def _candidate(source: dict[str, Any], query: str, root: Path) -> dict[str, Any]:
    normalized_query = _normalize(query)
    semantic_terms = _semantic_terms(query)
    score = 0
    reasons: list[str] = []
    labels = [source.get("profile", ""), source.get("database", ""), Path(str(source.get("path", ""))).stem]
    labels.extend(source.get("aliases", []))
    for label in labels:
        normalized = _normalize(label)
        if normalized and normalized in normalized_query:
            score += 12
            reasons.append(f"matched source label: {label}")
    matched_assets: list[str] = []
    matched_columns: list[str] = []
    semantic_matches: set[str] = set()
    for asset in source.get("assets", []):
        name = str(asset.get("name", ""))
        if _normalize(name) and _normalize(name) in normalized_query:
            score += 8
            matched_assets.append(name)
        asset_text = _normalize(f"{name} {asset.get('description', '')}")
        semantic_matches.update(term for term in semantic_terms if _normalize(term) in asset_text)
        for column in asset.get("columns", []):
            column_name = str(column.get("name", ""))
            if len(_normalize(column_name)) >= 2 and _normalize(column_name) in normalized_query:
                score += 3
                matched_columns.append(column_name)
            column_text = _normalize(f"{column_name} {column.get('description', '')}")
            semantic_matches.update(term for term in semantic_terms if _normalize(term) in column_text)
    if matched_assets:
        reasons.append(f"matched assets: {', '.join(matched_assets[:5])}")
    if matched_columns:
        reasons.append(f"matched columns: {', '.join(matched_columns[:8])}")
    if semantic_matches:
        score += min(10, len(semantic_matches) * 2)
        reasons.append(f"matched business terms: {', '.join(sorted(semantic_matches)[:8])}")
    if source.get("last_query") and _normalize(source["last_query"]) in normalized_query:
        score += 2
        reasons.append("matched prior usage")
    status = _source_status(source, root)
    if status == "active" and source.get("last_used_at"):
        score += 1
    return {
        "id": source.get("id"),
        "kind": source.get("kind"),
        "status": status,
        "score": score,
        "reasons": reasons,
        "profile": source.get("profile"),
        "path": source.get("path"),
        "database": source.get("database"),
        "access": source.get("access"),
        "matched_assets": matched_assets,
        "matched_columns": matched_columns,
    }


def resolve_sources(query: str, project_root: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    root = discover_project_root(project_root)
    context = load_context(root)
    sources = list(context["sources"])
    known_ids = {str(source.get("id")) for source in sources}
    indexed_database_identities = {
        (source.get("db_type"), source.get("database"), source.get("db_schema"))
        for source in sources
        if source.get("kind") == "database" and source.get("status") == "active"
    }
    sources.extend(
        source
        for source in _configured_profile_sources(root)
        if source["id"] not in known_ids
        and (source.get("db_type"), source.get("database"), source.get("db_schema"))
        not in indexed_database_identities
    )
    candidates = sorted(
        (_candidate(source, query, root) for source in sources),
        key=lambda item: (-item["score"], item["id"] or ""),
    )
    if not candidates:
        status = "not_found"
        selected = None
    elif len(candidates) == 1:
        selected = candidates[0]
        selected["reasons"] = selected["reasons"] or ["only active project data source"]
        status = "resolved" if selected["status"] == "active" else "needs_refresh"
    elif candidates[0]["score"] >= 5 and (
        len(candidates) == 1 or candidates[0]["score"] - candidates[1]["score"] >= 3
    ):
        selected = candidates[0]
        status = "needs_refresh" if selected["status"] in {"needs_refresh", "stale", "missing"} else "resolved"
    else:
        status = "ambiguous"
        selected = None
    return {
        "project_root": str(root),
        "context_path": str(get_context_path(root)),
        "query": query,
        "status": status,
        "selected": selected,
        "candidates": candidates[:10],
        "instruction": (
            "Use the selected source and record it with touch."
            if status == "resolved"
            else "Refresh the leading stale/unindexed source or ask the user to choose among candidates."
            if status in {"needs_refresh", "ambiguous"}
            else "Register the data file or database profile before analysis."
        ),
    }


def touch_source(
    source_id: str,
    *,
    query: str = "",
    project_root: str | os.PathLike[str] | None = None,
) -> Path:
    root = discover_project_root(project_root)
    context = load_context(root)
    source = next((item for item in context["sources"] if item.get("id") == source_id), None)
    if source is None:
        raise KeyError(f"Unknown project data source: {source_id}")
    source["last_used_at"] = _now()
    source["use_count"] = int(source.get("use_count", 0)) + 1
    if query:
        source["last_query"] = query
    return save_context(context, root)


def validate_context(project_root: str | os.PathLike[str] | None = None) -> list[str]:
    root = discover_project_root(project_root)
    context = load_context(root)
    errors: list[str] = []
    ids: set[str] = set()
    forbidden_keys = {"password", "username", "host", "connection_string", "uri", "sample", "sample_values"}

    def find_forbidden_keys(value: Any, prefix: str = "") -> list[str]:
        found: list[str] = []
        if isinstance(value, dict):
            for key, child in value.items():
                path = f"{prefix}.{key}" if prefix else str(key)
                if str(key).lower() in forbidden_keys:
                    found.append(path)
                found.extend(find_forbidden_keys(child, path))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                found.extend(find_forbidden_keys(child, f"{prefix}[{index}]"))
        return found
    for index, source in enumerate(context.get("sources", [])):
        source_id = source.get("id")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"sources[{index}].id is required")
        elif source_id in ids:
            errors.append(f"duplicate source id: {source_id}")
        else:
            ids.add(source_id)
        present_forbidden = find_forbidden_keys(source)
        if present_forbidden:
            errors.append(f"{source_id}: forbidden sensitive keys: {sorted(present_forbidden)}")
        if source.get("kind") not in {"database", "file"}:
            errors.append(f"{source_id}: invalid kind")
        if source.get("kind") == "file" and _source_status(source, root) != "active":
            errors.append(f"{source_id}: file is missing or changed; refresh it")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", help="Project root; defaults to nearest .git/.echart-skill ancestor")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show = subparsers.add_parser("show", help="Show the project data source index")
    show.set_defaults(action="show")

    resolve = subparsers.add_parser("resolve", help="Rank known project data sources for an analysis request")
    resolve.add_argument("--query", required=True)
    resolve.set_defaults(action="resolve")

    refresh_db = subparsers.add_parser("refresh-db", help="Discover tables and structure for a configured profile")
    refresh_db.add_argument("profile")
    refresh_db.add_argument("--max-assets", type=int, default=200)
    refresh_db.add_argument("--skip-row-counts", action="store_true")
    refresh_db.set_defaults(action="refresh_db")

    register = subparsers.add_parser("register-file", help="Persist a structure-only summary for a used data file")
    register.add_argument("path")
    register.add_argument("--duckdb")
    register.add_argument("--table", action="append", default=[])
    register.add_argument("--sample-rows", type=int, default=2000)
    register.set_defaults(action="register_file")

    touch = subparsers.add_parser("touch", help="Record successful use of a selected source")
    touch.add_argument("source_id")
    touch.add_argument("--query", default="")
    touch.set_defaults(action="touch")

    validate = subparsers.add_parser("validate", help="Validate source freshness and privacy invariants")
    validate.set_defaults(action="validate")

    args = parser.parse_args()
    root = args.project_root
    try:
        if args.action == "show":
            print(json.dumps(load_context(root), ensure_ascii=False, indent=2))
        elif args.action == "resolve":
            print(json.dumps(resolve_sources(args.query, root), ensure_ascii=False, indent=2))
        elif args.action == "refresh_db":
            source, path = refresh_database_source(
                args.profile,
                project_root=root,
                max_assets=args.max_assets,
                include_row_counts=not args.skip_row_counts,
            )
            print(json.dumps({
                "saved": str(path),
                "source_id": source["id"],
                "status": source["status"],
                "asset_count": source["asset_count"],
                "indexed_asset_count": source["indexed_asset_count"],
                "truncated": source["truncated"],
            }, ensure_ascii=False, indent=2))
        elif args.action == "register_file":
            source, path = register_file_source(
                args.path,
                project_root=root,
                duckdb_path=args.duckdb,
                table_names=args.table,
                sample_rows=args.sample_rows,
            )
            print(json.dumps({
                "saved": str(path),
                "source_id": source["id"],
                "status": source["status"],
                "access": source["access"],
                "assets": [asset["name"] for asset in source["assets"]],
            }, ensure_ascii=False, indent=2))
        elif args.action == "touch":
            print(touch_source(args.source_id, query=args.query, project_root=root))
        elif args.action == "validate":
            errors = validate_context(root)
            if errors:
                print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, indent=2))
                return 1
            print(json.dumps({"valid": True, "path": str(get_context_path(root))}, ensure_ascii=False, indent=2))
    except (FileNotFoundError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
