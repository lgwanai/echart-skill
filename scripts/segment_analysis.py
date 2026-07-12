"""Segment analysis for local DuckDB tables."""

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
class SegmentRow:
    segment: str
    row_count: int
    metric_value: float
    share_pct: float


@dataclass
class SegmentReport:
    table: str
    dimension: str
    metric: str
    agg: str
    total_value: float
    generated_at: str
    rows: list[SegmentRow] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def analyze_segments(
    table: str,
    dimension: str,
    metric: str,
    db_path: str = "workspace.duckdb",
    agg: str = "sum",
    limit: int = 20,
) -> SegmentReport:
    agg = agg.lower()
    if agg not in {"sum", "avg", "count"}:
        raise ValueError("agg must be sum, avg, or count")
    repo = get_repository(db_path)
    metric_expr = "*" if agg == "count" else _quote(metric)
    rows = repo.execute_query_raw(
        f"""
        SELECT
            COALESCE(CAST({_quote(dimension)} AS VARCHAR), '(null)') AS segment,
            COUNT(*) AS row_count,
            {agg.upper()}({metric_expr}) AS metric_value
        FROM {_quote(table)}
        GROUP BY 1
        ORDER BY metric_value DESC NULLS LAST
        LIMIT ?
        """,
        (limit,),
    )
    total_row = repo.execute_query_raw(f"SELECT {agg.upper()}({metric_expr}) AS value FROM {_quote(table)}")[0]
    total_value = float(total_row["value"] or 0)
    segment_rows = []
    for row in rows:
        value = float(row["metric_value"] or 0)
        share_pct = 0.0 if total_value == 0 else round(value / total_value * 100, 2)
        segment_rows.append(SegmentRow(
            segment=str(row["segment"]),
            row_count=int(row["row_count"]),
            metric_value=value,
            share_pct=share_pct,
        ))
    return SegmentReport(
        table=table,
        dimension=dimension,
        metric=metric,
        agg=agg,
        total_value=total_value,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        rows=segment_rows,
    )


def render_segment_markdown(report: SegmentReport) -> str:
    lines = [
        "# 分群分析",
        "",
        f"- 表: `{report.table}`",
        f"- 分群字段: `{report.dimension}`",
        f"- 指标: `{report.agg.upper()}({report.metric})`",
        f"- 总值: {report.total_value:.2f}",
        f"- 生成时间: {report.generated_at}",
        "",
        "| 分群 | 行数 | 指标值 | 占比 |",
        "|---|---:|---:|---:|",
    ]
    for row in report.rows:
        lines.append(f"| {row.segment} | {row.row_count} | {row.metric_value:.2f} | {row.share_pct:.2f}% |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="执行本地分群分析")
    parser.add_argument("table")
    parser.add_argument("dimension")
    parser.add_argument("metric")
    parser.add_argument("--db", default="workspace.duckdb")
    parser.add_argument("--agg", choices=["sum", "avg", "count"], default="sum")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    report = analyze_segments(args.table, args.dimension, args.metric, args.db, args.agg, args.limit)
    if args.format == "json":
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_segment_markdown(report))


if __name__ == "__main__":  # pragma: no cover
    main()
