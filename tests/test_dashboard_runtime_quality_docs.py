from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_runtime_quality_gate_exists_and_covers_recent_failure_modes():
    doc = (ROOT / "workflow_specs/dashboard_runtime_quality.md").read_text()

    required_terms = [
        "script.src",
        "fetch(\"https://",
        "var window.dashboardCharts",
        "chinaGeoJSON",
        "effectScatter",
        "color-mix",
        "html2canvas",
        "ignoreElements",
        "window.jspdf.jsPDF",
        "window.print()",
        "file://",
        "downloadChart",
        "validate_chart.py",
        "chart bootstrap scripts before the inlined ECharts library",
        "raw line breaks inside JavaScript string literals",
    ]

    for term in required_terms:
        assert term in doc


def test_dashboard_workflow_requires_runtime_quality_gate():
    workflow = (ROOT / "workflow_specs/dashboard_workflow.md").read_text()

    assert "workflow_specs/dashboard_runtime_quality.md" in workflow
    assert "file://" in workflow
    assert "color-mix()" in workflow


def test_skill_and_readme_expose_runtime_quality_gate():
    skill = (ROOT / "SKILL.md").read_text()
    readme = (ROOT / "README.md").read_text()

    for content in (skill, readme):
        assert "workflow_specs/dashboard_runtime_quality.md" in content
        assert "chinaGeoJSON" in content
        assert "color-mix()" in content
