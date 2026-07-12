"""Heuristic review gate for generated BI dashboard HTML files."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class DashboardReviewIssue:
    severity: str
    category: str
    title: str
    recommendation: str


@dataclass
class DashboardReview:
    dashboard_path: str
    score: int
    generated_at: str
    issues: list[DashboardReviewIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _penalty(issue: DashboardReviewIssue) -> int:
    return {"critical": 25, "high": 14, "medium": 7, "low": 3}.get(issue.severity, 3)


def review_dashboard(dashboard_path: str) -> DashboardReview:
    path = Path(dashboard_path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    lower = text.lower()
    issues: list[DashboardReviewIssue] = []
    external_refs = re.findall(r"""(?:src|href)=["']https?://""", text, flags=re.IGNORECASE)
    echarts_init_count = len(re.findall(r"echarts\.init\s*\(", text))
    chart_container_count = len(re.findall(r"""<div[^>]+id=["'][^"']+["'][^>]*>""", text, flags=re.IGNORECASE))
    kpi_mentions = sum(lower.count(token) for token in ("kpi", "指标", "总览", "summary"))
    insight_mentions = sum(text.count(token) for token in ("洞察", "结论", "异常", "建议", "风险"))
    has_title = bool(re.search(r"<title>.+?</title>|<h1[^>]*>.+?</h1>", text, flags=re.IGNORECASE | re.DOTALL))

    if external_refs:
        issues.append(DashboardReviewIssue("critical", "security", "存在外部网络资源引用", "企业离线交付 Dashboard 必须内联本地资源，移除 http/https src/href。"))
    if echarts_init_count == 0:
        issues.append(DashboardReviewIssue("high", "visualization", "未检测到 ECharts 初始化", "确认 Dashboard 至少包含一个可渲染的 ECharts 图表。"))
    if chart_container_count < echarts_init_count:
        issues.append(DashboardReviewIssue("medium", "runtime", "图表容器数量可能不足", "确保每个 echarts.init 都有稳定尺寸的 DOM 容器。"))
    if not has_title:
        issues.append(DashboardReviewIssue("medium", "structure", "缺少标题", "为 Dashboard 增加业务标题、统计范围和更新时间。"))
    if kpi_mentions == 0:
        issues.append(DashboardReviewIssue("medium", "business", "缺少 KPI 总览信号", "企业 Dashboard 首屏应包含关键指标或经营总览。"))
    if insight_mentions == 0:
        issues.append(DashboardReviewIssue("low", "analysis", "缺少洞察或风险提示", "补充关键结论、异常解释或行动建议，避免只有图表堆叠。"))
    if len(text) < 2000:
        issues.append(DashboardReviewIssue("low", "completeness", "文件内容偏短", "检查是否生成了完整 HTML、样式和图表配置。"))

    score = max(0, 100 - sum(_penalty(issue) for issue in issues))
    return DashboardReview(
        dashboard_path=str(path.resolve()),
        score=score,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        issues=issues,
        metrics={
            "external_ref_count": len(external_refs),
            "echarts_init_count": echarts_init_count,
            "chart_container_count": chart_container_count,
            "kpi_mentions": kpi_mentions,
            "insight_mentions": insight_mentions,
            "has_title": has_title,
            "file_size_chars": len(text),
        },
    )


def render_dashboard_review_markdown(review: DashboardReview) -> str:
    lines = [
        "# Dashboard 质量审阅",
        "",
        f"- 文件: `{review.dashboard_path}`",
        f"- 评分: {review.score} / 100",
        f"- 生成时间: {review.generated_at}",
        "",
        "## 问题",
        "",
    ]
    if not review.issues:
        lines.append("未发现明显 Dashboard 质量问题。")
        return "\n".join(lines) + "\n"
    lines.append("| 严重级别 | 类型 | 问题 | 建议 |")
    lines.append("|---|---|---|---|")
    for issue in review.issues:
        lines.append(f"| {issue.severity} | {issue.category} | {issue.title} | {issue.recommendation} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="审阅 Dashboard HTML 的离线性、图表和业务完整性")
    parser.add_argument("dashboard", help="Dashboard HTML 文件路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", help="输出路径")
    parser.add_argument("--print", action="store_true", help="同时打印结果")
    args = parser.parse_args()

    review = review_dashboard(args.dashboard)
    content = json.dumps(review.to_dict(), ensure_ascii=False, indent=2) if args.format == "json" else render_dashboard_review_markdown(review)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    if args.print or not args.output:
        print(content)


if __name__ == "__main__":  # pragma: no cover
    main()
