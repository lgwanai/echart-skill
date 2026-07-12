"""Heuristic review gate for generated BI reports."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ReviewIssue:
    severity: str
    category: str
    title: str
    recommendation: str


@dataclass
class ReportReview:
    report_path: str
    score: int
    generated_at: str
    issues: list[ReviewIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["issues"] = [asdict(issue) for issue in self.issues]
        return data


def _penalty(issue: ReviewIssue) -> int:
    return {"critical": 25, "high": 14, "medium": 7, "low": 3}.get(issue.severity, 3)


def review_report(report_path: str) -> ReportReview:
    path = Path(report_path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    lower = text.lower()
    issues: list[ReviewIssue] = []
    number_count = len(re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?%?", text))
    heading_count = len(re.findall(r"^#{1,3}\s+", text, flags=re.MULTILINE))
    table_count = text.count("\n|")
    chart_mentions = sum(lower.count(token) for token in ("echarts", "chart", "图表", "dashboard"))
    action_mentions = sum(text.count(token) for token in ("建议", "行动", "下一步", "策略", "优化"))
    limitation_mentions = sum(text.count(token) for token in ("限制", "口径", "样本", "置信", "假设"))

    if number_count < 5:
        issues.append(ReviewIssue("high", "evidence", "数字证据不足", "补充核心指标、同比/环比、占比、样本量等可核验数字。"))
    if heading_count < 3:
        issues.append(ReviewIssue("medium", "structure", "报告结构过弱", "使用摘要、数据概览、关键发现、归因、行动建议等清晰层级。"))
    if table_count == 0 and chart_mentions == 0:
        issues.append(ReviewIssue("high", "visual-evidence", "缺少图表或附录表证据", "为主要结论增加图表、表格或附录数据引用。"))
    if action_mentions == 0:
        issues.append(ReviewIssue("medium", "decision", "缺少行动建议", "把发现转化为负责人可执行的业务动作和优先级。"))
    if limitation_mentions == 0:
        issues.append(ReviewIssue("medium", "governance", "缺少口径/限制说明", "说明统计口径、样本范围、缺失处理和结论置信度。"))
    if any(token in text for token in ("显著提升", "巨大潜力", "非常优秀", "明显领先")) and number_count < 10:
        issues.append(ReviewIssue("low", "tone", "存在未充分举证的强判断", "把强结论改成带证据和边界的企业报告表达。"))

    score = max(0, 100 - sum(_penalty(issue) for issue in issues))
    return ReportReview(
        report_path=str(path.resolve()),
        score=score,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        issues=issues,
        metrics={
            "number_count": number_count,
            "heading_count": heading_count,
            "table_count": table_count,
            "chart_mentions": chart_mentions,
            "action_mentions": action_mentions,
            "limitation_mentions": limitation_mentions,
        },
    )


def render_review_markdown(review: ReportReview) -> str:
    lines = [
        "# 报告质量审阅",
        "",
        f"- 报告: `{review.report_path}`",
        f"- 评分: {review.score} / 100",
        f"- 生成时间: {review.generated_at}",
        "",
        "## 问题",
        "",
    ]
    if not review.issues:
        lines.append("未发现明显报告质量问题。")
        return "\n".join(lines) + "\n"
    lines.append("| 严重级别 | 类型 | 问题 | 建议 |")
    lines.append("|---|---|---|---|")
    for issue in review.issues:
        lines.append(f"| {issue.severity} | {issue.category} | {issue.title} | {issue.recommendation} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="审阅生成报告的专业性、证据和治理完整性")
    parser.add_argument("report", help="报告文件路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", help="输出路径")
    parser.add_argument("--print", action="store_true", help="同时打印结果")
    args = parser.parse_args()

    review = review_report(args.report)
    content = json.dumps(review.to_dict(), ensure_ascii=False, indent=2) if args.format == "json" else render_review_markdown(review)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    if args.print or not args.output:
        print(content)


if __name__ == "__main__":  # pragma: no cover
    main()
