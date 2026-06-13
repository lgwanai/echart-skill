"""
Report Engine — Automated Analysis Report Generation.

This module generates professional analysis reports from data insights,
supporting Markdown, HTML, and PDF output formats. It combines the Insight
Engine's structured findings with chart visualizations to produce
comprehensive, human-readable reports.

Architecture:
    Insights + Charts + Template → Structured Report → Multi-format Output

Usage:
    from scripts.report_engine import ReportEngine

    engine = ReportEngine("workspace.duckdb")
    report_path = engine.generate(
        table="sales",
        title="销售数据分析报告",
        output_format="html",
    )
"""

import json
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

import duckdb

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_repository
from logging_config import get_logger
from scripts.insight_engine import InsightEngine, Insight, InsightType, Severity, TableProfile

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Report data structures
# ---------------------------------------------------------------------------

@dataclass
class ReportSection:
    """A section within an analysis report."""
    heading: str
    level: int = 2  # Markdown heading level
    content: str = ""
    insights: list[Insight] = field(default_factory=list)
    subsections: list["ReportSection"] = field(default_factory=list)


@dataclass
class Report:
    """Complete analysis report."""
    title: str
    subtitle: str = ""
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    sections: list[ReportSection] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Report Templates
# ---------------------------------------------------------------------------

REPORT_TEMPLATES = {
    "general": {
        "name": "通用数据分析报告",
        "description": "适用于各类数据表的通用分析报告模板",
        "sections": [
            {"heading": "报告摘要", "slug": "executive-summary"},
            {"heading": "数据概览", "slug": "data-overview"},
            {"heading": "关键指标分析", "slug": "key-metrics"},
            {"heading": "维度分析", "slug": "dimension-analysis"},
            {"heading": "趋势分析", "slug": "trend-analysis"},
            {"heading": "异常发现", "slug": "anomaly-findings"},
            {"heading": "相关性分析", "slug": "correlation-analysis"},
            {"heading": "建议与下一步", "slug": "recommendations"},
        ],
    },
    "sales": {
        "name": "销售分析报告",
        "description": "适用于销售数据的分析报告模板",
        "sections": [
            {"heading": "报告摘要", "slug": "executive-summary"},
            {"heading": "销售概况", "slug": "sales-overview"},
            {"heading": "产品销售分析", "slug": "product-analysis"},
            {"heading": "渠道与支付分析", "slug": "channel-analysis"},
            {"heading": "区域分析", "slug": "region-analysis"},
            {"heading": "趋势与预测", "slug": "trend-forecast"},
            {"heading": "问题与建议", "slug": "recommendations"},
        ],
    },
    "quick": {
        "name": "快速分析摘要",
        "description": "简洁的单页分析摘要，适合快速了解数据",
        "sections": [
            {"heading": "核心发现", "slug": "key-findings"},
            {"heading": "数据画像", "slug": "data-profile"},
            {"heading": "关键洞察", "slug": "key-insights"},
            {"heading": "行动建议", "slug": "actions"},
        ],
    },
}


# ---------------------------------------------------------------------------
# Report Engine
# ---------------------------------------------------------------------------

class ReportEngine:
    """Automated analysis report generator.

    This engine combines the Insight Engine's pattern discovery with
    professional report templates to produce comprehensive analysis
    reports in multiple formats.

    Attributes:
        db_path: Path to the DuckDB database file.
        insight_engine: InsightEngine instance for analysis.
        output_dir: Directory for generated reports.
    """

    def __init__(
        self,
        db_path: str = "workspace.duckdb",
        output_dir: str = "outputs/reports",
    ):
        """Initialize the report engine.

        Args:
            db_path: Path to the DuckDB database file.
            output_dir: Directory for generated reports.
        """
        self.db_path = db_path
        self.insight_engine = InsightEngine(db_path)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        table: str,
        title: Optional[str] = None,
        template: str = "general",
        output_format: str = "markdown",
        output_path: Optional[str] = None,
        sections: Optional[list[str]] = None,
        include_charts: bool = True,
        **analysis_kwargs,
    ) -> str:
        """Generate a full analysis report.

        Args:
            table: Name of the table to analyze.
            title: Report title (auto-generated if None).
            template: Report template name ("general", "sales", "quick").
            output_format: Output format ("markdown", "html", "json").
            output_path: Output file path (auto-generated if None).
            sections: Specific sections to include (all if None).
            include_charts: Whether to include chart suggestions in the report.
            **analysis_kwargs: Additional args passed to InsightEngine.analyze().

        Returns:
            Path to the generated report file.
        """
        logger.info("开始生成报告", table=table, template=template)

        # Step 1: Profile & analyze
        profile = self.insight_engine.profile_table(table)
        if profile is None:
            raise ValueError(f"表 '{table}' 不存在或无法读取")

        insights = self.insight_engine.analyze(table, **analysis_kwargs)

        # Step 2: Build report structure from template
        template_config = REPORT_TEMPLATES.get(template, REPORT_TEMPLATES["general"])
        if title is None:
            title = f"{table} — {template_config['name']}"

        report = Report(
            title=title,
            subtitle=f"基于 {profile.row_count} 条数据的自动分析",
        )

        # Step 3: Fill sections
        section_slugs = sections or [s["slug"] for s in template_config["sections"]]

        for section_config in template_config["sections"]:
            if section_config["slug"] not in section_slugs:
                continue

            section = self._build_section(
                section_config["slug"],
                section_config["heading"],
                profile,
                insights,
                include_charts,
            )
            if section:
                report.sections.append(section)

        # Step 4: Generate output
        if output_path is None:
            safe_table = table.replace("/", "_").replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = {"markdown": ".md", "html": ".html", "json": ".json"}[output_format]
            output_path = os.path.join(
                self.output_dir, f"{safe_table}_{template}_{timestamp}{ext}"
            )

        if output_format == "markdown":
            self._write_markdown(report, output_path, include_charts)
        elif output_format == "html":
            self._write_html(report, output_path, include_charts)
        elif output_format == "json":
            self._write_json(report, insights, output_path)

        logger.info("报告生成完成", path=output_path)
        return output_path

    def quick_report(
        self,
        table: str,
        output_format: str = "markdown",
    ) -> str:
        """Generate a quick summary report (fast mode).

        Args:
            table: Name of the table to analyze.
            output_format: Output format.

        Returns:
            Path to the generated report file.
        """
        return self.generate(
            table=table,
            template="quick",
            output_format=output_format,
            top_n=3,
            include_summary=True,
        )

    # ------------------------------------------------------------------
    # Section Builders
    # ------------------------------------------------------------------

    def _build_section(
        self,
        slug: str,
        heading: str,
        profile: TableProfile,
        insights: list[Insight],
        include_charts: bool,
    ) -> Optional[ReportSection]:
        """Build a report section from insights matching the slug."""

        # Route to specific builders
        builders = {
            "executive-summary": self._build_executive_summary,
            "data-overview": self._build_data_overview,
            "key-metrics": self._build_key_metrics,
            "dimension-analysis": self._build_dimension_analysis,
            "trend-analysis": self._build_trend_analysis,
            "anomaly-findings": self._build_anomaly_findings,
            "correlation-analysis": self._build_correlation_analysis,
            "recommendations": self._build_recommendations,
            # Sales template
            "sales-overview": self._build_data_overview,
            "product-analysis": self._build_dimension_analysis,
            "channel-analysis": self._build_dimension_analysis,
            "region-analysis": self._build_dimension_analysis,
            "trend-forecast": self._build_trend_analysis,
            # Quick template
            "key-findings": self._build_executive_summary,
            "data-profile": self._build_data_overview,
            "key-insights": self._build_dimension_analysis,
            "actions": self._build_recommendations,
        }

        builder = builders.get(slug)
        if builder:
            return builder(heading, profile, insights, include_charts)

        # Generic: collect matching insights
        return self._build_generic_section(heading, insights, include_charts)

    def _build_executive_summary(
        self,
        heading: str,
        profile: TableProfile,
        insights: list[Insight],
        include_charts: bool,
    ) -> ReportSection:
        """Build the executive summary section."""
        section = ReportSection(heading=heading, level=2)

        # Pick the most important insights
        high_severity = [
            i for i in insights
            if i.severity in (Severity.CRITICAL, Severity.HIGH)
        ][:3]

        summary_points = []
        # Key facts from profile
        summary_points.append(
            f"本报告基于 **{profile.table_name}** 表的 {profile.row_count:,} 条记录，"
            f"涵盖 {profile.column_count} 个字段。"
        )

        for insight in high_severity:
            summary_points.append(insight.description)

        # If we have trends, mention the direction
        trends = [i for i in insights if i.type == InsightType.TREND]
        anomalies = [i for i in insights if i.type == InsightType.ANOMALY]

        if anomalies:
            summary_points.append(
                f"⚠️ 检测到 {len(anomalies)} 个异常数据点，建议重点关注。"
            )

        section.content = "\n\n".join(f"- {p}" for p in summary_points)
        section.insights = high_severity

        return section

    def _build_data_overview(
        self,
        heading: str,
        profile: TableProfile,
        insights: list[Insight],
        include_charts: bool,
    ) -> ReportSection:
        """Build the data overview section."""
        section = ReportSection(heading=heading, level=2)

        lines = []
        lines.append(f"| 属性 | 值 |")
        lines.append(f"|------|-----|")
        lines.append(f"| 表名 | {profile.table_name} |")
        lines.append(f"| 行数 | {profile.row_count:,} |")
        lines.append(f"| 列数 | {profile.column_count} |")

        if profile.date_columns:
            lines.append(f"| 日期列 | {', '.join(profile.date_columns)} |")
        if profile.metric_columns:
            lines.append(f"| 数值列 | {', '.join(profile.metric_columns)} |")
        if profile.category_columns:
            lines.append(f"| 分类列 | {', '.join(profile.category_columns)} |")
        if profile.geo_columns:
            lines.append(f"| 地理列 | {', '.join(profile.geo_columns)} |")

        section.content = "\n".join(lines)

        # Add column details
        col_lines = ["\n### 字段详情\n"]
        col_lines.append("| 字段 | 类型 | 缺失率 | 唯一值数 |")
        col_lines.append("|------|------|--------|----------|")
        for c in profile.columns:
            col_lines.append(
                f"| {c.name} | {c.dtype} | {c.null_pct}% | {c.unique_count:,} |"
            )
        section.content += "\n" + "\n".join(col_lines)

        summary_insights = [i for i in insights if i.type == InsightType.SUMMARY]
        section.insights = summary_insights

        return section

    def _build_key_metrics(
        self,
        heading: str,
        profile: TableProfile,
        insights: list[Insight],
        include_charts: bool,
    ) -> ReportSection:
        """Build the key metrics section with KPI-style cards."""
        section = ReportSection(heading=heading, level=2)

        metric_cols = profile.metric_columns[:5]
        lines = ["| 指标 | 均值 | 中位数 | 最小值 | 最大值 | 标准差 |"]
        lines.append("|------|------|--------|--------|--------|--------|")

        for mc in metric_cols:
            col = next((c for c in profile.columns if c.name == mc), None)
            if col and col.mean is not None:
                lines.append(
                    f"| {col.name} | {col.mean:.1f} | {col.median:.1f} | "
                    f"{col.min_val:.1f} | {col.max_val:.1f} | {col.std:.1f} |"
                )

        section.content = "\n".join(lines)

        related = [
            i for i in insights
            if i.type in (InsightType.SUMMARY, InsightType.CHANGE)
            and any(c in profile.metric_columns for c in i.related_columns)
        ]
        section.insights = related

        return section

    def _build_dimension_analysis(
        self,
        heading: str,
        profile: TableProfile,
        insights: list[Insight],
        include_charts: bool,
    ) -> ReportSection:
        """Build dimension analysis section from ranking & composition insights."""
        section = ReportSection(heading=heading, level=2)

        ranking = [i for i in insights if i.type == InsightType.RANKING]
        composition = [i for i in insights if i.type == InsightType.COMPOSITION]

        # Group by dimension
        dim_groups: dict[str, list[Insight]] = {}
        for ins in ranking + composition:
            dim = ins.evidence.get("dimension", "其他")
            if dim not in dim_groups:
                dim_groups[dim] = []
            dim_groups[dim].append(ins)

        lines = []
        for dim, dim_insights in dim_groups.items():
            lines.append(f"### {dim}\n")
            for ins in dim_insights[:3]:
                lines.append(f"**{ins.title}**\n")
                lines.append(f"{ins.description}\n")

        section.content = "\n".join(lines)
        section.insights = ranking + composition

        return section

    def _build_trend_analysis(
        self,
        heading: str,
        profile: TableProfile,
        insights: list[Insight],
        include_charts: bool,
    ) -> ReportSection:
        """Build trend analysis section."""
        section = ReportSection(heading=heading, level=2)

        trends = [i for i in insights if i.type == InsightType.TREND]
        changes = [i for i in insights if i.type == InsightType.CHANGE]
        seasonality = [i for i in insights if i.type == InsightType.SEASONALITY]

        lines = []

        if trends:
            lines.append("### 整体趋势\n")
            for ins in trends:
                lines.append(f"- **{ins.title}**：{ins.description}")

        if changes:
            lines.append("\n### 周期对比\n")
            for ins in changes:
                lines.append(f"- **{ins.title}**：{ins.description}")

        if seasonality:
            lines.append("\n### 季节性规律\n")
            for ins in seasonality:
                lines.append(f"- **{ins.title}**：{ins.description}")

        section.content = "\n".join(lines)
        section.insights = trends + changes + seasonality

        return section

    def _build_anomaly_findings(
        self,
        heading: str,
        profile: TableProfile,
        insights: list[Insight],
        include_charts: bool,
    ) -> ReportSection:
        """Build anomaly findings section."""
        section = ReportSection(heading=heading, level=2)

        anomalies = [i for i in insights if i.type == InsightType.ANOMALY]

        if not anomalies:
            section.content = "✅ 未检测到显著异常数据点。"
            return section

        lines = [f"检测到 **{len(anomalies)}** 个异常数据点：\n"]
        lines.append("| 时间 | 指标 | 异常描述 | 严重程度 |")
        lines.append("|------|------|----------|----------|")

        sev_labels = {
            Severity.CRITICAL: "🔴 严重",
            Severity.HIGH: "🟠 重要",
            Severity.MEDIUM: "🟡 中等",
        }

        for ins in anomalies:
            period = ins.evidence.get("period", "N/A")
            metric = ins.evidence.get("metric", "N/A")
            sev = sev_labels.get(ins.severity, "低")
            lines.append(f"| {period} | {metric} | {ins.description[:60]}... | {sev} |")

        section.content = "\n".join(lines)
        section.insights = anomalies

        return section

    def _build_correlation_analysis(
        self,
        heading: str,
        profile: TableProfile,
        insights: list[Insight],
        include_charts: bool,
    ) -> ReportSection:
        """Build correlation analysis section."""
        section = ReportSection(heading=heading, level=2)

        correlations = [i for i in insights if i.type == InsightType.CORRELATION]

        if not correlations:
            section.content = "未检测到显著相关性。"
            return section

        lines = ["| 指标 A | 指标 B | 相关系数 | 方向 | 强度 |"]
        lines.append("|--------|--------|----------|------|------|")

        for ins in correlations:
            ev = ins.evidence
            lines.append(
                f"| {ev.get('column_a', 'N/A')} | {ev.get('column_b', 'N/A')} | "
                f"{ev.get('correlation', 'N/A')} | {ev.get('direction', 'N/A')} | "
                f"{ev.get('strength', 'N/A')} |"
            )

        section.content = "\n".join(lines)
        section.insights = correlations

        return section

    def _build_recommendations(
        self,
        heading: str,
        profile: TableProfile,
        insights: list[Insight],
        include_charts: bool,
    ) -> ReportSection:
        """Generate actionable recommendations based on insights."""
        section = ReportSection(heading=heading, level=2)

        recommendations = []

        # Check for high-severity anomalies → recommend investigation
        anomalies = [i for i in insights if i.type == InsightType.ANOMALY
                     and i.severity in (Severity.CRITICAL, Severity.HIGH)]
        if anomalies:
            cols = ", ".join(set(
                c for ins in anomalies for c in ins.related_columns
            ))
            recommendations.append(
                f"🔍 **深入调查异常数据**：建议对 {cols} 的 {len(anomalies)} 处异常值进行根因分析。"
            )

        # Check for negative trends → recommend action
        negative_trends = [
            i for i in insights
            if i.type == InsightType.TREND and "下降" in i.description
        ]
        if negative_trends:
            recommendations.append(
                f"📉 **关注下降趋势**：部分指标呈下降趋势，建议分析下降原因并制定应对方案。"
            )

        # Check concentration → recommend diversification
        high_conc = [
            i for i in insights
            if i.type == InsightType.COMPOSITION and i.severity == Severity.HIGH
        ]
        if high_conc:
            recommendations.append(
                f"📊 **优化集中度风险**：部分维度过于集中，建议考虑多元化策略以分散风险。"
            )

        # Check data quality
        high_null = [c for c in profile.columns if c.null_pct >= 20]
        if high_null:
            recommendations.append(
                f"🧹 **提升数据质量**：{len(high_null)} 个字段缺失率超过 20%，建议完善数据采集流程。"
            )

        # Positive findings
        positive_trends = [
            i for i in insights
            if i.type == InsightType.TREND and "增长" in i.description
        ]
        if positive_trends:
            recommendations.append(
                f"✅ **巩固增长趋势**：部分指标呈现良好增长态势，建议总结经验并推广。"
            )

        if not recommendations:
            recommendations.append(
                "基于当前数据，暂无特别需要关注的问题。建议持续监控关键指标变化。"
            )

        section.content = "\n\n".join(f"{i+1}. {r}" for i, r in enumerate(recommendations))

        return section

    def _build_generic_section(
        self,
        heading: str,
        insights: list[Insight],
        include_charts: bool,
    ) -> ReportSection:
        """Build a generic section from any matching insights."""
        section = ReportSection(heading=heading, level=2)
        matching = insights[:5]  # take first 5

        if not matching:
            section.content = "暂无相关发现。"
            return section

        lines = []
        for ins in matching:
            lines.append(f"### {ins.title}\n")
            lines.append(f"{ins.description}\n")
            if include_charts and ins.suggested_chart:
                lines.append(f"📈 *建议图表类型: {ins.suggested_chart}*\n")

        section.content = "\n".join(lines)
        section.insights = matching

        return section

    # ------------------------------------------------------------------
    # Output Formats
    # ------------------------------------------------------------------

    def _write_markdown(
        self,
        report: Report,
        output_path: str,
        include_charts: bool,
    ):
        """Write report as Markdown."""
        lines = []

        # Title
        lines.append(f"# {report.title}\n")
        if report.subtitle:
            lines.append(f"*{report.subtitle}*\n")
        lines.append(f"> 生成时间: {report.generated_at[:19]}\n")
        lines.append("---\n")

        # Table of contents
        lines.append("## 目录\n")
        for s in report.sections:
            anchor = s.heading.lower().replace(" ", "-")
            lines.append(f"- [{s.heading}](#{anchor})")
        lines.append("")

        # Sections
        for section in report.sections:
            lines.append(f"{'#' * section.level} {section.heading}\n")
            if section.content:
                lines.append(section.content)
                lines.append("")

            # Inline insights
            for ins in section.insights:
                lines.append(f"> **{ins.title}**")
                lines.append(f"> {ins.description}")
                if include_charts and ins.suggested_chart:
                    lines.append(f"> 📈 推荐图表: `{ins.suggested_chart}`")
                lines.append("")

        # Footer
        lines.append("---\n")
        lines.append(f"*报告由 Agent BI 自动生成 | {report.generated_at[:19]}*\n")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_html(
        self,
        report: Report,
        output_path: str,
        include_charts: bool,
    ):
        """Write report as styled HTML."""
        # First write as markdown, then convert basic
        md_path = output_path.replace(".html", ".md")
        self._write_markdown(report, md_path, include_charts)

        # Simple HTML wrapper with styling
        # This produces a clean, readable HTML report
        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="zh-CN">',
            "<head>",
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f"<title>{report.title}</title>",
            "<style>",
            """
            :root {
                --bg: #ffffff; --text: #1a1a2e; --muted: #6b7280;
                --accent: #3b82f6; --border: #e5e7eb; --card: #f9fafb;
                --critical: #ef4444; --high: #f59e0b; --medium: #3b82f6; --low: #9ca3af;
            }
            @media (prefers-color-scheme: dark) {
                :root {
                    --bg: #0f172a; --text: #e2e8f0; --muted: #94a3b8;
                    --accent: #60a5fa; --border: #1e293b; --card: #1e293b;
                }
            }
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: var(--bg); color: var(--text);
                line-height: 1.7; max-width: 900px; margin: 0 auto; padding: 2rem;
            }
            h1 { font-size: 2rem; margin-bottom: 0.5rem; }
            h2 { font-size: 1.5rem; margin-top: 2.5rem; margin-bottom: 1rem;
                 padding-bottom: 0.5rem; border-bottom: 2px solid var(--accent); }
            h3 { font-size: 1.2rem; margin-top: 1.5rem; margin-bottom: 0.5rem; }
            p { margin-bottom: 1rem; }
            .subtitle { color: var(--muted); font-size: 1rem; margin-bottom: 0.5rem; }
            .timestamp { color: var(--muted); font-size: 0.85rem; margin-bottom: 1.5rem; }
            table { width: 100%; border-collapse: collapse; margin: 1rem 0 1.5rem; }
            th, td { padding: 0.5rem 1rem; text-align: left; border: 1px solid var(--border); }
            th { background: var(--card); font-weight: 600; }
            tr:nth-child(even) { background: var(--card); }
            blockquote {
                border-left: 4px solid var(--accent);
                margin: 1rem 0; padding: 0.75rem 1rem;
                background: var(--card); border-radius: 0 8px 8px 0;
            }
            blockquote p { margin-bottom: 0.25rem; }
            .severity-critical { border-left-color: var(--critical); }
            .severity-high { border-left-color: var(--high); }
            .severity-medium { border-left-color: var(--medium); }
            hr { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }
            .footer { color: var(--muted); font-size: 0.85rem; text-align: center; }
            .badge {
                display: inline-block; padding: 0.15rem 0.5rem;
                border-radius: 12px; font-size: 0.75rem; font-weight: 600;
                margin-right: 0.25rem;
            }
            .badge-critical { background: #fef2f2; color: #dc2626; }
            .badge-high { background: #fffbeb; color: #d97706; }
            .badge-medium { background: #eff6ff; color: #2563eb; }
            .badge-low { background: #f3f4f6; color: #6b7280; }
            ul, ol { margin: 0.5rem 0 1rem 1.5rem; }
            li { margin-bottom: 0.25rem; }
            @media (max-width: 768px) {
                body { padding: 1rem; }
                table { font-size: 0.85rem; }
                th, td { padding: 0.35rem 0.5rem; }
            }
            </style>""",
            "</head>",
            "<body>",
            f"<h1>{report.title}</h1>",
        ]

        if report.subtitle:
            html_parts.append(f'<p class="subtitle">{report.subtitle}</p>')
        html_parts.append(
            f'<p class="timestamp">📅 生成时间: {report.generated_at[:19]}</p>'
        )

        # Build sections
        for section in report.sections:
            h_tag = f"h{section.level}"
            html_parts.append(f"<{h_tag}>{section.heading}</{h_tag}>")

            if section.content:
                # Simple markdown-to-html for common patterns
                content = section.content
                # Convert tables
                content = self._md_to_html(content)
                html_parts.append(content)

            # Insight blocks
            for ins in section.insights:
                sev_class = f"severity-{ins.severity.value}"
                badge_class = f"badge-{ins.severity.value}"
                html_parts.append(
                    f'<blockquote class="{sev_class}">'
                    f'<strong>{ins.title}</strong>'
                    f'<span class="badge {badge_class}">{ins.severity.value}</span>'
                    f"<p>{ins.description}</p>"
                )
                if include_charts and ins.suggested_chart:
                    html_parts.append(
                        f'<p style="font-size:0.85rem;color:var(--muted)">'
                        f'📈 推荐图表: {ins.suggested_chart}</p>'
                    )
                html_parts.append("</blockquote>")

        html_parts.append("<hr>")
        html_parts.append(
            f'<p class="footer">📊 报告由 <strong>Agent BI</strong> 自动生成 | '
            f'{report.generated_at[:19]}</p>'
        )
        html_parts.append("</body></html>")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(html_parts))

    def _write_json(
        self,
        report: Report,
        insights: list[Insight],
        output_path: str,
    ):
        """Write report as structured JSON."""
        output = {
            "title": report.title,
            "subtitle": report.subtitle,
            "generated_at": report.generated_at,
            "sections": [
                {
                    "heading": s.heading,
                    "level": s.level,
                    "content": s.content,
                    "insights": [i.to_dict() for i in s.insights],
                }
                for s in report.sections
            ],
            "all_insights": [i.to_dict() for i in insights],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

    def _md_to_html(self, text: str) -> str:
        """Basic markdown-to-HTML conversion for report content."""
        import re

        # Tables: keep as-is
        if "|" in text:
            # Wrap tables in proper HTML
            lines = text.split("\n")
            in_table = False
            result = []
            for line in lines:
                if "|" in line and line.strip().startswith("|"):
                    if not in_table:
                        result.append("<table>")
                        in_table = True
                    cells = [c.strip() for c in line.split("|")[1:-1]]
                    tag = "th" if "---" in line else "td"
                    # Skip separator rows
                    if all(c.replace("-", "").replace(":", "").strip() == "" for c in cells):
                        continue
                    result.append(
                        "<tr>"
                        + "".join(f"<{tag}>{c}</{tag}>" for c in cells)
                        + "</tr>"
                    )
                else:
                    if in_table:
                        result.append("</table>")
                        in_table = False
                    if line.strip():
                        result.append(f"<p>{line}</p>")
            if in_table:
                result.append("</table>")
            return "\n".join(result)

        # Basic formatting
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

        # Lists
        lines = text.split("\n")
        result = []
        in_list = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- "):
                if not in_list:
                    result.append("<ul>")
                    in_list = True
                result.append(f"<li>{stripped[2:]}</li>")
            elif stripped.startswith(("1. ", "2. ", "3. ")):
                if not in_list:
                    result.append("<ol>")
                    in_list = True
                result.append(f"<li>{stripped[3:]}</li>")
            else:
                if in_list:
                    result.append("</ul>" if "<ul>" in result[-1] else "</ol>")
                    in_list = False
                if stripped:
                    result.append(f"<p>{stripped}</p>")
        if in_list:
            result.append("</ul>")
        return "\n".join(result)


# ---------------------------------------------------------------------------
# CLI Interface
# ---------------------------------------------------------------------------

def main():
    """Command-line entry point for the report engine."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Report Engine — Automated analysis report generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/report_engine.py sales
  python scripts/report_engine.py sales --template sales --format html
  python scripts/report_engine.py sales --quick --format markdown
        """,
    )
    parser.add_argument("table", help="Table name to analyze and report")
    parser.add_argument("--title", "-t", help="Report title (auto-generated if omitted)")
    parser.add_argument("--template", choices=list(REPORT_TEMPLATES.keys()),
                       default="general", help="Report template")
    parser.add_argument("--format", "-f", choices=["markdown", "html", "json"],
                       default="markdown", help="Output format")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--quick", action="store_true", help="Quick report mode")
    parser.add_argument("--db", default="workspace.duckdb", help="Database path")

    args = parser.parse_args()

    engine = ReportEngine(db_path=args.db)

    try:
        if args.quick:
            path = engine.quick_report(args.table, output_format=args.format)
        else:
            path = engine.generate(
                table=args.table,
                title=args.title,
                template=args.template,
                output_format=args.format,
                output_path=args.output,
            )
        print(f"✅ 报告已生成: {path}")
        if args.format in ("markdown", "html"):
            print(f"📂 在浏览器中打开: file://{os.path.abspath(path)}")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
