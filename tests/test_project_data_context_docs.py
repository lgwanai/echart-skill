from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_skill_routes_source_discovery_through_project_context():
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "workflow_specs/project_data_context.md" in skill
    assert "project_data_context.py resolve" in skill
    assert ".echart-skill/data_sources.json" in skill


def test_analysis_commands_resolve_source_before_querying():
    for name in ("query", "analyze", "insight", "chart", "dashboard", "report", "dbconn", "import"):
        command = (ROOT / "commands" / "echart" / f"{name}.md").read_text(encoding="utf-8")
        assert "project_data_context.py resolve" in command, name


def test_workflow_keeps_context_project_owned_and_credential_free():
    workflow = (ROOT / "workflow_specs/project_data_context.md").read_text(encoding="utf-8")
    assert "<project>/.echart-skill/data_sources.json" in workflow
    assert "must never contain hosts, usernames, passwords" in workflow
    assert "ambiguous" in workflow
    assert "do not silently select" in workflow
