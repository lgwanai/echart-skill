"""Funnel conversion analysis for local DuckDB event tables."""

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
class FunnelStep:
    step: str
    users: int
    from_start_pct: float
    from_previous_pct: float
    dropoff_users: int


@dataclass
class FunnelReport:
    table: str
    user_column: str
    step_column: str
    generated_at: str
    steps: list[FunnelStep] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def analyze_funnel(
    table: str,
    user_column: str,
    step_column: str,
    steps: list[str],
    db_path: str = "workspace.duckdb",
) -> FunnelReport:
    if not steps:
        raise ValueError("steps must not be empty")
    repo = get_repository(db_path)
    counts = []
    for step in steps:
        row = repo.execute_query_raw(
            f"""
            SELECT COUNT(DISTINCT {_quote(user_column)}) AS users
            FROM {_quote(table)}
            WHERE CAST({_quote(step_column)} AS VARCHAR) = ?
            """,
            (step,),
        )[0]
        counts.append(int(row["users"] or 0))

    start = counts[0]
    previous = start
    result_steps: list[FunnelStep] = []
    for step, users in zip(steps, counts):
        from_start = 0.0 if start == 0 else round(users / start * 100, 2)
        from_previous = 0.0 if previous == 0 else round(users / previous * 100, 2)
        result_steps.append(FunnelStep(
            step=step,
            users=users,
            from_start_pct=from_start,
            from_previous_pct=from_previous,
            dropoff_users=max(previous - users, 0),
        ))
        previous = users

    return FunnelReport(
        table=table,
        user_column=user_column,
        step_column=step_column,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        steps=result_steps,
    )


def render_funnel_markdown(report: FunnelReport) -> str:
    lines = [
        "# 漏斗分析",
        "",
        f"- 表: `{report.table}`",
        f"- 用户字段: `{report.user_column}`",
        f"- 步骤字段: `{report.step_column}`",
        f"- 生成时间: {report.generated_at}",
        "",
        "| 步骤 | 用户数 | 相对首步转化 | 相对上步转化 | 上步流失人数 |",
        "|---|---:|---:|---:|---:|",
    ]
    for step in report.steps:
        lines.append(
            f"| {step.step} | {step.users} | {step.from_start_pct:.2f}% | "
            f"{step.from_previous_pct:.2f}% | {step.dropoff_users} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="执行本地漏斗转化分析")
    parser.add_argument("table")
    parser.add_argument("user_column")
    parser.add_argument("step_column")
    parser.add_argument("--steps", required=True, help="漏斗步骤，逗号分隔且按顺序排列")
    parser.add_argument("--db", default="workspace.duckdb")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    steps = [item.strip() for item in args.steps.split(",") if item.strip()]
    report = analyze_funnel(args.table, args.user_column, args.step_column, steps, args.db)
    if args.format == "json":
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_funnel_markdown(report))


if __name__ == "__main__":  # pragma: no cover
    main()
