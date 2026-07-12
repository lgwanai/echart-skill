"""Cohort retention analysis for local DuckDB activity tables."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database import get_repository


@dataclass
class CohortCell:
    cohort: str
    period_index: int
    users: int
    retention_pct: float


@dataclass
class CohortReport:
    table: str
    user_column: str
    cohort_date_column: str
    activity_date_column: str
    unit: str
    generated_at: str
    cells: list[CohortCell] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def analyze_cohort(
    table: str,
    user_column: str,
    cohort_date_column: str,
    activity_date_column: str,
    db_path: str = "workspace.duckdb",
    unit: str = "month",
    max_period: int = 12,
) -> CohortReport:
    if unit not in {"day", "week", "month"}:
        raise ValueError("unit must be day, week, or month")
    repo = get_repository(db_path)
    rows = repo.execute_query_raw(
        f"""
        WITH base AS (
            SELECT
                {_quote(user_column)} AS user_id,
                DATE_TRUNC('{unit}', CAST({_quote(cohort_date_column)} AS DATE)) AS cohort,
                DATE_TRUNC('{unit}', CAST({_quote(activity_date_column)} AS DATE)) AS activity_period
            FROM {_quote(table)}
            WHERE {_quote(user_column)} IS NOT NULL
              AND {_quote(cohort_date_column)} IS NOT NULL
              AND {_quote(activity_date_column)} IS NOT NULL
        ),
        counted AS (
            SELECT
                CAST(CAST(cohort AS DATE) AS VARCHAR) AS cohort,
                DATE_DIFF('{unit}', cohort, activity_period) AS period_index,
                COUNT(DISTINCT user_id) AS users
            FROM base
            WHERE activity_period >= cohort
            GROUP BY 1, 2
        ),
        sizes AS (
            SELECT cohort, users AS cohort_users
            FROM counted
            WHERE period_index = 0
        )
        SELECT
            counted.cohort,
            counted.period_index,
            counted.users,
            ROUND(counted.users * 100.0 / NULLIF(sizes.cohort_users, 0), 2) AS retention_pct
        FROM counted
        JOIN sizes USING (cohort)
        WHERE counted.period_index <= ?
        ORDER BY counted.cohort, counted.period_index
        """,
        (max_period,),
    )
    cells = [
        CohortCell(
            cohort=str(row["cohort"]),
            period_index=int(row["period_index"]),
            users=int(row["users"]),
            retention_pct=float(row["retention_pct"] or 0),
        )
        for row in rows
    ]
    return CohortReport(
        table=table,
        user_column=user_column,
        cohort_date_column=cohort_date_column,
        activity_date_column=activity_date_column,
        unit=unit,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        cells=cells,
    )


def render_cohort_markdown(report: CohortReport) -> str:
    periods = sorted({cell.period_index for cell in report.cells})
    cohorts = sorted({cell.cohort for cell in report.cells})
    lookup = {(cell.cohort, cell.period_index): cell for cell in report.cells}
    lines = [
        "# 留存/队列分析",
        "",
        f"- 表: `{report.table}`",
        f"- 用户字段: `{report.user_column}`",
        f"- 队列日期字段: `{report.cohort_date_column}`",
        f"- 活跃日期字段: `{report.activity_date_column}`",
        f"- 周期: {report.unit}",
        f"- 生成时间: {report.generated_at}",
        "",
    ]
    if not periods:
        lines.append("无可用队列数据。")
        return "\n".join(lines) + "\n"
    lines.append("| 队列 | " + " | ".join(f"P{period}" for period in periods) + " |")
    lines.append("|---" + "|---:" * len(periods) + "|")
    for cohort in cohorts:
        values = []
        for period in periods:
            cell = lookup.get((cohort, period))
            values.append("" if cell is None else f"{cell.retention_pct:.2f}% ({cell.users})")
        lines.append(f"| {cohort} | " + " | ".join(values) + " |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="执行本地留存/队列分析")
    parser.add_argument("table")
    parser.add_argument("user_column")
    parser.add_argument("cohort_date_column")
    parser.add_argument("activity_date_column")
    parser.add_argument("--db", default="workspace.duckdb")
    parser.add_argument("--unit", choices=["day", "week", "month"], default="month")
    parser.add_argument("--max-period", type=int, default=12)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    report = analyze_cohort(
        args.table,
        args.user_column,
        args.cohort_date_column,
        args.activity_date_column,
        args.db,
        args.unit,
        args.max_period,
    )
    if args.format == "json":
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_cohort_markdown(report))


if __name__ == "__main__":  # pragma: no cover
    main()
