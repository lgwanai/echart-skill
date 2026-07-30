"""Parameterized analysis query runner for echart-skill.

Agents may write SQL files for unusual questions, but routine BI requests
should call this tool instead of producing temporary Python scripts. The tool
builds reviewable SQL for common analyses and executes it through sql_runner's
audited connection path.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.audit_report import log_command
from scripts.sql_runner import (
    _execute_duckdb,
    _execute_external_connection_args,
    _execute_external_dsn,
    _execute_external_profile,
    _format_rows,
    _write_output,
)


IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
AGGREGATIONS = {"sum", "avg", "count", "count_distinct", "min", "max"}


def _quote_identifier(name: str) -> str:
    if not IDENTIFIER_RE.match(name):
        raise SystemExit(f"Error: unsafe identifier {name!r}. Use a real table/column name, not SQL fragments.")
    return '"' + name.replace('"', '""') + '"'


def _date_expr(column: str) -> str:
    return f"CAST({_quote_identifier(column)} AS DATE)"


def _quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _split_assignment(raw: str, flag: str) -> tuple[str, str]:
    if "=" not in raw:
        raise SystemExit(f"Error: {flag} expects column=value, got {raw!r}")
    column, value = raw.split("=", 1)
    column = column.strip()
    value = value.strip()
    if not column or not value:
        raise SystemExit(f"Error: {flag} expects non-empty column=value")
    return column, value


def _metric_expr(metric: str, agg: str) -> str:
    agg = agg.lower()
    if agg not in AGGREGATIONS:
        raise SystemExit(f"Error: agg must be one of {', '.join(sorted(AGGREGATIONS))}")
    if agg == "count":
        return "COUNT(*)"
    if agg == "count_distinct":
        return f"COUNT(DISTINCT {_quote_identifier(metric)})"
    return f"{agg.upper()}({_quote_identifier(metric)})"


def _where_clause(base_filter: str | None) -> str:
    if not base_filter:
        return ""
    forbidden = re.search(r";|--|/\*|\*/|\b(drop|delete|insert|update|alter|create|truncate)\b", base_filter, re.IGNORECASE)
    if forbidden:
        raise SystemExit("Error: --where only accepts a read-only boolean filter without semicolons/comments/DML.")
    return f" AND ({base_filter})"


def _structured_filter_clause(args: argparse.Namespace) -> str:
    filters = []
    for raw in args.eq or []:
        column, value = _split_assignment(raw, "--eq")
        filters.append(f"{_quote_identifier(column)} = {_quote_literal(value)}")
    for raw in args.contains or []:
        column, value = _split_assignment(raw, "--contains")
        filters.append(f"CAST({_quote_identifier(column)} AS VARCHAR) LIKE {_quote_literal('%' + value + '%')}")
    for raw in args.contains_any or []:
        column, values = _split_assignment(raw, "--contains-any")
        parts = [
            f"CAST({_quote_identifier(column)} AS VARCHAR) LIKE {_quote_literal('%' + value.strip() + '%')}"
            for value in values.split(",")
            if value.strip()
        ]
        if parts:
            filters.append("(" + " OR ".join(parts) + ")")
    for raw in args.or_eq or []:
        column, values = _split_assignment(raw, "--or-eq")
        parts = [
            f"{_quote_identifier(column)} = {_quote_literal(value.strip())}"
            for value in values.split(",")
            if value.strip()
        ]
        if parts:
            filters.append("(" + " OR ".join(parts) + ")")
    any_parts = []
    for raw in args.any_contains or []:
        column, values = _split_assignment(raw, "--any-contains")
        any_parts.extend(
            f"CAST({_quote_identifier(column)} AS VARCHAR) LIKE {_quote_literal('%' + value.strip() + '%')}"
            for value in values.split(",")
            if value.strip()
        )
    for raw in args.any_eq or []:
        column, values = _split_assignment(raw, "--any-eq")
        any_parts.extend(
            f"{_quote_identifier(column)} = {_quote_literal(value.strip())}"
            for value in values.split(",")
            if value.strip()
        )
    if any_parts:
        filters.append("(" + " OR ".join(any_parts) + ")")
    return "".join(f" AND ({condition})" for condition in filters)


def _all_filters(args: argparse.Namespace) -> str:
    return _where_clause(args.where) + _structured_filter_clause(args)


def build_period_compare_sql(args: argparse.Namespace) -> str:
    table = _quote_identifier(args.table)
    date_col = _date_expr(args.date_column)
    value_expr = _metric_expr(args.metric, args.agg)
    where = _all_filters(args)
    dimension_select = ""
    dimension_order = ""
    base_group_by = "GROUP BY 1"
    pivot_group_by = ""
    if args.dimension:
        dimension = _quote_identifier(args.dimension)
        dimension_select = f"COALESCE(CAST({dimension} AS VARCHAR), '(null)') AS dimension,"
        base_group_by = "GROUP BY 1, 2"
        pivot_group_by = "GROUP BY 1"
        dimension_order = "ORDER BY current_value DESC NULLS LAST"

    return f"""
WITH base AS (
  SELECT
    {dimension_select}
    CASE
      WHEN {date_col} >= DATE '{args.baseline_start}' AND {date_col} <= DATE '{args.baseline_end}' THEN 'baseline'
      WHEN {date_col} >= DATE '{args.current_start}' AND {date_col} <= DATE '{args.current_end}' THEN 'current'
    END AS period_bucket,
    {value_expr} AS metric_value
  FROM {table}
  WHERE (
    ({date_col} >= DATE '{args.baseline_start}' AND {date_col} <= DATE '{args.baseline_end}')
    OR ({date_col} >= DATE '{args.current_start}' AND {date_col} <= DATE '{args.current_end}')
  ){where}
  {base_group_by}
),
pivoted AS (
  SELECT
    {('dimension,' if args.dimension else '')}
    SUM(CASE WHEN period_bucket = 'baseline' THEN metric_value ELSE 0 END) AS baseline_value,
    SUM(CASE WHEN period_bucket = 'current' THEN metric_value ELSE 0 END) AS current_value
  FROM base
  {pivot_group_by}
)
SELECT
  {('dimension,' if args.dimension else '')}
  baseline_value,
  current_value,
  current_value - baseline_value AS absolute_change,
  CASE WHEN baseline_value = 0 THEN NULL ELSE ROUND((current_value - baseline_value) * 100.0 / baseline_value, 2) END AS pct_change
FROM pivoted
{dimension_order}
LIMIT {int(args.limit)}
""".strip()


def build_segment_sql(args: argparse.Namespace) -> str:
    value_expr = _metric_expr(args.metric, args.agg)
    where = _all_filters(args)
    return f"""
SELECT
  COALESCE(CAST({_quote_identifier(args.dimension)} AS VARCHAR), '(null)') AS dimension,
  COUNT(*) AS row_count,
  {value_expr} AS metric_value
FROM {_quote_identifier(args.table)}
WHERE 1 = 1{where}
GROUP BY 1
ORDER BY metric_value DESC NULLS LAST
LIMIT {int(args.limit)}
""".strip()


def build_trend_sql(args: argparse.Namespace) -> str:
    value_expr = _metric_expr(args.metric, args.agg)
    date_col = _date_expr(args.date_column)
    where = _all_filters(args)
    return f"""
SELECT
  DATE_TRUNC('{args.grain}', {date_col}) AS period,
  {value_expr} AS metric_value,
  COUNT(*) AS row_count
FROM {_quote_identifier(args.table)}
WHERE {date_col} >= DATE '{args.start}' AND {date_col} <= DATE '{args.end}'{where}
GROUP BY 1
ORDER BY 1
LIMIT {int(args.limit)}
""".strip()


def build_topn_sql(args: argparse.Namespace) -> str:
    value_expr = _metric_expr(args.metric, args.agg)
    where = _all_filters(args)
    return f"""
SELECT
  COALESCE(CAST({_quote_identifier(args.dimension)} AS VARCHAR), '(null)') AS dimension,
  {value_expr} AS metric_value,
  COUNT(*) AS row_count
FROM {_quote_identifier(args.table)}
WHERE 1 = 1{where}
GROUP BY 1
ORDER BY metric_value DESC NULLS LAST
LIMIT {int(args.limit)}
""".strip()


def build_entity_search_sql(args: argparse.Namespace) -> str:
    where = _all_filters(args)
    contains = ""
    if args.contains_text:
        contains = f" AND CAST({_quote_identifier(args.column)} AS VARCHAR) LIKE {_quote_literal('%' + args.contains_text + '%')}"
    return f"""
SELECT DISTINCT
  CAST({_quote_identifier(args.column)} AS VARCHAR) AS value
FROM {_quote_identifier(args.table)}
WHERE {_quote_identifier(args.column)} IS NOT NULL
  AND CAST({_quote_identifier(args.column)} AS VARCHAR) != ''
  {contains}{where}
ORDER BY 1
LIMIT {int(args.limit)}
""".strip()


def _execute(sql: str, args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.profile:
        return _execute_external_profile(sql, args.profile, args.config, args.allow_write)
    if args.dsn_env:
        return _execute_external_dsn(sql, args.dsn_env, args.type, args.allow_write)
    if args.host or args.database or args.username or args.password_env:
        return _execute_external_connection_args(sql, args)
    return _execute_duckdb(sql, args.db, args.allow_write)


def _run(args: argparse.Namespace) -> int:
    builders = {
        "entity-search": build_entity_search_sql,
        "period-compare": build_period_compare_sql,
        "segment": build_segment_sql,
        "trend": build_trend_sql,
        "topn": build_topn_sql,
    }
    sql = builders[args.command](args)
    if args.print_sql:
        print(sql)
        return 0
    log_command("analysis_runner", status="started", note=args.command)
    try:
        rows = _execute(sql, args)
        max_rows = args.max_rows if args.max_rows is not None else (0 if args.out else 200)
        _write_output(_format_rows(rows, args.output, max_rows), args.out or "")
        log_command("analysis_runner", status="completed", note=f"{args.command}: rows={len(rows)}")
        return 0
    except Exception as exc:
        log_command("analysis_runner", status="failed", note=str(exc)[:200])
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def _add_connection_args(parser: argparse.ArgumentParser) -> None:
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--db", default="workspace.duckdb", help="DuckDB path; default workspace.duckdb")
    source.add_argument("--profile", help="External SQL connection profile from /dbconn")
    source.add_argument("--dsn-env", help="Environment variable containing a SQLAlchemy DSN")
    parser.add_argument("--config", default="", help="Optional db_connections.txt path for --profile")
    parser.add_argument("--type", choices=["postgresql", "mysql"], default="", help="Database type for --dsn-env or direct connection parameters")
    parser.add_argument("--host", help="Direct SQL database host")
    parser.add_argument("--port", type=int, help="Direct SQL database port")
    parser.add_argument("--database", help="Direct SQL database name")
    parser.add_argument("--username", "--user", dest="username", help="Direct SQL database username")
    parser.add_argument("--password-env", help="Environment variable containing the direct SQL database password")
    parser.add_argument("--schema", help="Optional schema name for direct PostgreSQL connections")
    parser.add_argument("--timeout", type=float, default=30.0, help="Direct SQL connection timeout in seconds")
    parser.add_argument("--allow-write", action="store_true", help="Allow DDL/DML. Default is read-only.")
    parser.add_argument("--output", "-o", choices=["table", "json", "csv"], default="table")
    parser.add_argument("--out", help="Write formatted output to file")
    parser.add_argument("--max-rows", type=int, help="Max rows to render; default stdout=200, --out=all")
    parser.add_argument("--where", help="Optional read-only boolean SQL filter")
    parser.add_argument("--eq", action="append", help="Structured equality filter: column=value. Can be repeated.")
    parser.add_argument("--contains", action="append", help="Structured LIKE filter: column=text. Can be repeated.")
    parser.add_argument("--contains-any", action="append", help="Structured OR LIKE filter: column=text1,text2,text3. Can be repeated.")
    parser.add_argument("--or-eq", action="append", help="Structured OR equality filter: column=value1,value2. Can be repeated.")
    parser.add_argument("--any-contains", action="append", help="Shared OR-group LIKE filter: column=text1,text2. Combines with --any-eq.")
    parser.add_argument("--any-eq", action="append", help="Shared OR-group equality filter: column=value1,value2. Combines with --any-contains.")
    parser.add_argument("--print-sql", action="store_true", help="Print generated SQL without executing")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run parameterized BI analysis queries without temporary Python")
    subparsers = parser.add_subparsers(dest="command", required=True)

    entity = subparsers.add_parser("entity-search", help="Search distinct entity values such as hotels or demand customers")
    _add_connection_args(entity)
    entity.add_argument("--table", required=True)
    entity.add_argument("--column", required=True)
    entity.add_argument("--contains-text")
    entity.add_argument("--limit", type=int, default=100)

    period = subparsers.add_parser("period-compare", help="Compare metric between two date ranges, optionally by dimension")
    _add_connection_args(period)
    period.add_argument("--table", required=True)
    period.add_argument("--date-column", required=True)
    period.add_argument("--metric", required=True)
    period.add_argument("--agg", choices=sorted(AGGREGATIONS), default="sum")
    period.add_argument("--dimension")
    period.add_argument("--baseline-start", required=True)
    period.add_argument("--baseline-end", required=True)
    period.add_argument("--current-start", required=True)
    period.add_argument("--current-end", required=True)
    period.add_argument("--limit", type=int, default=200)

    segment = subparsers.add_parser("segment", help="Aggregate a metric by one dimension")
    _add_connection_args(segment)
    segment.add_argument("--table", required=True)
    segment.add_argument("--dimension", required=True)
    segment.add_argument("--metric", required=True)
    segment.add_argument("--agg", choices=sorted(AGGREGATIONS), default="sum")
    segment.add_argument("--limit", type=int, default=20)

    trend = subparsers.add_parser("trend", help="Aggregate a metric by day/month/quarter/year")
    _add_connection_args(trend)
    trend.add_argument("--table", required=True)
    trend.add_argument("--date-column", required=True)
    trend.add_argument("--metric", required=True)
    trend.add_argument("--agg", choices=sorted(AGGREGATIONS), default="sum")
    trend.add_argument("--grain", choices=["day", "month", "quarter", "year"], default="month")
    trend.add_argument("--start", required=True)
    trend.add_argument("--end", required=True)
    trend.add_argument("--limit", type=int, default=500)

    topn = subparsers.add_parser("topn", help="Top-N dimension ranking")
    _add_connection_args(topn)
    topn.add_argument("--table", required=True)
    topn.add_argument("--dimension", required=True)
    topn.add_argument("--metric", required=True)
    topn.add_argument("--agg", choices=sorted(AGGREGATIONS), default="sum")
    topn.add_argument("--limit", type=int, default=20)

    return parser


def main(argv: list[str] | None = None) -> int:
    return _run(create_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
