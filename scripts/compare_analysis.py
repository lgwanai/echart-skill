"""Metric comparison analysis for local DuckDB tables."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database import get_repository


@dataclass
class CompareResult:
    table: str
    metric: str
    group_column: str
    baseline: str
    current: str
    baseline_value: float
    current_value: float
    absolute_change: float
    pct_change: float | None
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def compare_metric(
    table: str,
    metric: str,
    group_column: str,
    baseline: str,
    current: str,
    db_path: str = "workspace.duckdb",
    agg: str = "sum",
) -> CompareResult:
    agg = agg.lower()
    if agg not in {"sum", "avg", "count"}:
        raise ValueError("agg must be sum, avg, or count")
    repo = get_repository(db_path)
    metric_expr = "*" if agg == "count" else _quote(metric)
    rows = repo.execute_query_raw(
        f"""
        SELECT CAST({_quote(group_column)} AS VARCHAR) AS grp, {agg.upper()}({metric_expr}) AS value
        FROM {_quote(table)}
        WHERE CAST({_quote(group_column)} AS VARCHAR) IN (?, ?)
        GROUP BY 1
        """,
        (baseline, current),
    )
    values = {row["grp"]: float(row["value"] or 0) for row in rows}
    baseline_value = values.get(baseline, 0.0)
    current_value = values.get(current, 0.0)
    absolute_change = current_value - baseline_value
    pct_change = None if baseline_value == 0 else round(absolute_change / baseline_value * 100, 2)
    return CompareResult(
        table=table,
        metric=metric,
        group_column=group_column,
        baseline=baseline,
        current=current,
        baseline_value=baseline_value,
        current_value=current_value,
        absolute_change=absolute_change,
        pct_change=pct_change,
        generated_at=datetime.now().isoformat(timespec="seconds"),
    )


def render_compare_markdown(result: CompareResult) -> str:
    pct = "不可计算" if result.pct_change is None else f"{result.pct_change:.2f}%"
    return "\n".join([
        "# 指标对比分析",
        "",
        f"- 表: `{result.table}`",
        f"- 指标: `{result.metric}`",
        f"- 分组字段: `{result.group_column}`",
        f"- 基准组: {result.baseline} = {result.baseline_value:.2f}",
        f"- 对比组: {result.current} = {result.current_value:.2f}",
        f"- 变化量: {result.absolute_change:.2f}",
        f"- 变化率: {pct}",
        f"- 生成时间: {result.generated_at}",
        "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description="执行本地指标对比分析")
    parser.add_argument("table")
    parser.add_argument("metric")
    parser.add_argument("group_column")
    parser.add_argument("baseline")
    parser.add_argument("current")
    parser.add_argument("--db", default="workspace.duckdb")
    parser.add_argument("--agg", choices=["sum", "avg", "count"], default="sum")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    result = compare_metric(args.table, args.metric, args.group_column, args.baseline, args.current, args.db, args.agg)
    if args.format == "json":
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_compare_markdown(result))


if __name__ == "__main__":  # pragma: no cover
    main()
