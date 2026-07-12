"""What-if scenario analysis for local metric aggregates."""

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
class ScenarioResult:
    name: str
    multiplier: float
    projected_value: float
    absolute_change: float
    pct_change: float


@dataclass
class WhatIfReport:
    table: str
    metric: str
    agg: str
    baseline_value: float
    generated_at: str
    scenarios: list[ScenarioResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _parse_scenarios(value: str) -> list[tuple[str, float]]:
    scenarios = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            name, raw = item.split(":", 1)
            pct = float(raw.strip().rstrip("%"))
        else:
            pct = float(item.rstrip("%"))
            name = f"{pct:+g}%"
        scenarios.append((name.strip(), pct / 100.0))
    return scenarios


def analyze_whatif(
    table: str,
    metric: str,
    scenarios: list[tuple[str, float]],
    db_path: str = "workspace.duckdb",
    agg: str = "sum",
) -> WhatIfReport:
    agg = agg.lower()
    if agg not in {"sum", "avg", "count"}:
        raise ValueError("agg must be sum, avg, or count")
    repo = get_repository(db_path)
    metric_expr = "*" if agg == "count" else _quote(metric)
    row = repo.execute_query_raw(f"SELECT {agg.upper()}({metric_expr}) AS value FROM {_quote(table)}")[0]
    baseline = float(row["value"] or 0)
    results = []
    for name, delta in scenarios:
        multiplier = 1 + delta
        projected = baseline * multiplier
        results.append(ScenarioResult(
            name=name,
            multiplier=round(multiplier, 6),
            projected_value=round(projected, 6),
            absolute_change=round(projected - baseline, 6),
            pct_change=round(delta * 100, 2),
        ))
    return WhatIfReport(
        table=table,
        metric=metric,
        agg=agg,
        baseline_value=baseline,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        scenarios=results,
    )


def render_whatif_markdown(report: WhatIfReport) -> str:
    lines = [
        "# 假设推演分析",
        "",
        f"- 表: `{report.table}`",
        f"- 指标: `{report.agg.upper()}({report.metric})`",
        f"- 基准值: {report.baseline_value:.2f}",
        f"- 生成时间: {report.generated_at}",
        "",
        "| 场景 | 变化率 | 推演值 | 变化量 |",
        "|---|---:|---:|---:|",
    ]
    for scenario in report.scenarios:
        lines.append(
            f"| {scenario.name} | {scenario.pct_change:.2f}% | "
            f"{scenario.projected_value:.2f} | {scenario.absolute_change:.2f} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="执行本地 What-if 假设推演")
    parser.add_argument("table")
    parser.add_argument("metric")
    parser.add_argument("--scenarios", required=True, help="场景列表，例如 conservative:-5,base:0,growth:10")
    parser.add_argument("--db", default="workspace.duckdb")
    parser.add_argument("--agg", choices=["sum", "avg", "count"], default="sum")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    report = analyze_whatif(args.table, args.metric, _parse_scenarios(args.scenarios), args.db, args.agg)
    if args.format == "json":
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_whatif_markdown(report))


if __name__ == "__main__":  # pragma: no cover
    main()
