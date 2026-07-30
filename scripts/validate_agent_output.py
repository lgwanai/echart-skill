"""Validate agent command/output logs against echart-skill execution policy.

This catches the recurring failure mode where an agent answers an analysis
request by pasting ad-hoc heredoc Python with direct database connections.
Database work must go through the maintained SQL runner / DB CLI so audit,
privacy, connection profiles, and output limits are consistently applied.
Agent-authored SQL may be passed directly with ``scripts/sql_runner.py --sql``
or saved as a SQL file and executed with ``scripts/sql_runner.py --file``.
The forbidden pattern is writing Python just to connect and execute SQL.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "HEREDOC_PYTHON",
        re.compile(r"\bpython3?\s+<<\s*['\"]?(?:PY|PYEOF|EOF)['\"]?", re.IGNORECASE),
        "Do not use heredoc Python for database/query execution.",
    ),
    (
        "DIRECT_POSTGRES_CONNECT",
        re.compile(r"\bpsycopg(?:2)?\s*\.\s*connect\s*\(", re.IGNORECASE),
        "Use `python scripts/sql_runner.py --profile <name> --sql \"<SELECT ...>\"` or direct sql_runner connection args instead of psycopg/psycopg2.connect.",
    ),
    (
        "DIRECT_POSTGRES_IMPORT",
        re.compile(r"^\s*(?:import\s+psycopg(?:2)?|from\s+psycopg(?:2)?\b)", re.IGNORECASE | re.MULTILINE),
        "Do not import psycopg/psycopg2 in agent-generated analysis. Write SQL and call scripts/sql_runner.py.",
    ),
    (
        "DIRECT_MYSQL_CONNECT",
        re.compile(r"\bpymysql\s*\.\s*connect\s*\(", re.IGNORECASE),
        "Use `python scripts/sql_runner.py --profile <name> --sql \"<SELECT ...>\"` or direct sql_runner connection args instead of pymysql.connect.",
    ),
    (
        "DIRECT_MYSQL_IMPORT",
        re.compile(r"^\s*(?:import\s+pymysql|from\s+pymysql\b)", re.IGNORECASE | re.MULTILINE),
        "Do not import pymysql in agent-generated analysis. Write SQL and call scripts/sql_runner.py.",
    ),
    (
        "DIRECT_SQLALCHEMY_ENGINE",
        re.compile(r"\bcreate_engine\s*\(", re.IGNORECASE),
        "Use configured profiles or `--dsn-env` through scripts/sql_runner.py instead of ad-hoc create_engine.",
    ),
    (
        "DIRECT_DUCKDB_CONNECT",
        re.compile(r"\bduckdb\s*\.\s*connect\s*\(", re.IGNORECASE),
        "Do not open DuckDB connections in agent-generated query code. Use scripts/sql_runner.py --db ... --sql/--file.",
    ),
    (
        "DIRECT_CONN_VARIABLE",
        re.compile(r"^\s*(?:conn|connection|engine|session)\s*=", re.IGNORECASE | re.MULTILINE),
        "Agent output must not start database work from `conn = ...`, `engine = ...`, or similar handles; write SQL and execute it with scripts/sql_runner.py or another maintained DB tool.",
    ),
    (
        "DIRECT_CURSOR",
        re.compile(r"\.\s*cursor\s*\(", re.IGNORECASE),
        "Agent-generated query code must not create cursors. Use scripts/sql_runner.py/db_cli.py for SQL execution.",
    ),
    (
        "DIRECT_CURSOR_EXECUTE",
        re.compile(r"\b(?:cur|cursor)\s*\.\s*execute\s*\(", re.IGNORECASE),
        "Agent-generated query code must not execute SQL through cursor objects. Use scripts/sql_runner.py --sql or --file.",
    ),
)


def validate_text(text: str) -> list[str]:
    errors: list[str] = []
    for code, pattern, message in FORBIDDEN_PATTERNS:
        for match in pattern.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            errors.append(f"{code} at line {line_no}: {message}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate agent logs against echart-skill execution policy")
    parser.add_argument("path", help="Text/log file to scan")
    args = parser.parse_args(argv)

    text = Path(args.path).read_text(encoding="utf-8")
    errors = validate_text(text)
    if errors:
        print("INVALID agent output: forbidden database execution pattern detected.", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print(
            "\nRepair by writing SQL from the schema and effective scope definitions, then execute it with "
            "`python scripts/sql_runner.py --profile <name> --sql \"<SELECT ...>\" --output json` "
            "or `python scripts/sql_runner.py --profile <name> --file queries/<task>.sql --output json` "
            "or `python scripts/sql_runner.py --type postgresql --host <host> --database <db> "
            "--username <user> --password-env DB_PASSWORD --sql \"<SELECT ...>\" --output json`. "
            "Use analysis code only for work SQL cannot express; it must not own database connections or SQL execution.",
            file=sys.stderr,
        )
        return 1

    print("OK: no forbidden agent execution patterns detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
