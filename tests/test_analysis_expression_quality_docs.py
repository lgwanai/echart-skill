from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_expression_contract_is_routed_from_core_workflows():
    required_files = [
        ROOT / "SKILL.md",
        ROOT / "references/knowledge/INDEX.md",
        ROOT / "workflow_specs/dashboard_workflow.md",
        ROOT / "workflow_specs/report_workflow.md",
        ROOT / "commands/echart/chart.md",
        ROOT / "commands/echart/dashboard.md",
        ROOT / "commands/echart/analyze.md",
        ROOT / "commands/echart/insight.md",
        ROOT / "commands/echart/report.md",
    ]
    for path in required_files:
        text = path.read_text(encoding="utf-8")
        assert "analysis_expression_quality.md" in text, path


def test_expression_contract_covers_selection_tables_and_drilldown():
    text = (ROOT / "workflow_specs/analysis_expression_quality.md").read_text(encoding="utf-8")
    for phrase in (
        "Message → Relation → View",
        "Relationship-to-view matrix",
        "source_toggle",
        "companion",
        "primary",
        "What",
        "Baseline",
        "Why status",
        "So what",
        "Next check",
        "validate_analysis_plan.py",
        "Period alignment is a blocking gate",
        "latest_complete_period_end",
    ):
        assert phrase in text
