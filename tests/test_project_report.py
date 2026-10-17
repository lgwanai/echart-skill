import copy
import json
from pathlib import Path

import pytest

from scripts import project_report as pr
from scripts.sql_runner import main as query_main


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def project(tmp_path, monkeypatch):
    root = tmp_path / "project"
    folder = root / "config/reports"
    folder.mkdir(parents=True)
    monkeypatch.chdir(root)
    monkeypatch.delenv("ECHART_PROJECT_ROOT", raising=False)
    profile = {"version": 1, "audience": "经营管理层",
               "analysis": {"methods": [{"id": "ranking", "instructions": "按金额排序并核对总额"}], "questions": ["金额集中在哪里？"]},
               "layout": {"columns": 2, "accent": "#146358", "wide_charts": ["rank"],
                          "sections": [{"id": "summary", "title": "管理摘要"}, {"id": "findings", "title": "核心发现"}]},
               "charts": {"preferences": {"ranking": "bar"}, "avoid": ["pie"]}}
    write(folder / "management.json", profile)
    write(folder / "manifest.json", {"version": 1, "default": "management", "profiles": {"management": "config/reports/management.json"}})
    query_main(["--db", str(root / "data.duckdb"), "--sql",
                "SELECT * FROM (VALUES ('North',20), ('South',10)) t(region,amount) ORDER BY amount DESC",
                "--output", "json", "--out", str(root / "results/amount.json")])
    metadata = json.loads((root / "results/amount.json.meta.json").read_text())
    qhash = metadata["query_hash"]
    plan = {"audience": "经营管理层", "decision_context": "Review concentration", "analysis_mode": "decision_support",
            "questions": ["金额集中在哪里？"], "views": [{"id": "rank", "message": "North contributes 20 of 30", "relation": "ranking",
                "primary_view": "bar", "reason": "Compare category magnitudes", "evidence_ref": "q1",
                "rejected_alternatives": [{"view": "pie", "reason": "Precise ranking needs aligned lengths"}],
                "table_mode": "companion", "table_reason": "核对金额", "table_columns": ["region", "amount"]}],
            "findings": [{"id": "f1", "importance": "major", "what": "North contributes 20 of 30", "baseline": "Total 30",
                "why_status": "hypothesis", "why": "Underlying driver not established", "so_what": "Review concentration",
                "next_check": "Collect product detail", "evidence_refs": ["q1"], "limitations": ["Only two categories"]}]}
    document = {"artifact_type": "report", "report": {"title": "经营分析", "scope": "按区域汇总金额，共2个区域，合计30元",
        "limitations": ["只有区域汇总，不能判断因果关系"], "profile_sha256": pr.resolve()["sha256"],
        "sections": [{"id": "findings", "paragraphs": ["North为20元，占合计30元的三分之二。"], "evidence_query_ids": ["q1"]},
                     {"id": "summary", "paragraphs": ["North 20元，South 10元，应核查收入集中度。"], "evidence_query_ids": ["q1"]}],
        "methods": [{"id": "ranking", "status": "executed", "evidence_query_ids": ["q1"], "note": "按金额排序，汇总为30元"}]},
        "analysis_plan": plan, "charts": [{"id": "rank", "title": "区域金额排名", "scope": "按区域汇总，单位元",
            "section": "findings", "source": "q1", "query_hash": qhash, "rows_path": "results/amount.json", "x": "region",
            "metrics": [{"field": "amount", "name": "金额", "unit": "元"}]}]}
    draft = {"queries": [{"id": "q1", "result_path": "results/amount.json", "query_hash": qhash}],
             "findings": [{"id": "f1", "evidence_query_ids": ["q1"], "why_status": "hypothesis"}]}
    write(root / "report.json", document)
    write(root / "evidence.json", draft)
    return root, profile, document, draft


def prepared(project, *, overrides=None):
    from scripts.artifact_manifest import materialize_manifest
    root, _, doc, draft = project
    resolved = pr.resolve(overrides=overrides)
    evidence = materialize_manifest(draft, root / "evidence.json", root / "report.html")
    return pr.prepare(doc, root, resolved, evidence)


def test_profile_discovery_defaults_and_nested_project(project, monkeypatch):
    root, _, _, _ = project
    nested = root / "outputs/deep"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    resolved = pr.resolve()
    assert resolved["project_root"] == str(root)
    assert resolved["profile"] == "management"
    assert resolved["settings"]["layout"]["columns"] == 2
    assert resolved["settings"]["analysis"]["methods"][0]["id"] == "ranking"


def test_no_profiles_uses_builtin_without_writes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ECHART_PROJECT_ROOT", raising=False)
    assert pr.resolve()["profile"] == "builtin"
    assert not (tmp_path / "config").exists()


def test_project_isolation(project, tmp_path, monkeypatch):
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(other)
    assert pr.resolve()["profile"] == "builtin"
    monkeypatch.setenv("ECHART_PROJECT_ROOT", str(project[0]))
    assert pr.resolve()["profile"] == "management"


def test_multiple_profiles_require_default_or_selection(project):
    root = project[0]
    write(root / pr.MANIFEST, {"version": 1, "profiles": {"a": "config/reports/management.json", "b": "config/reports/management.json"}})
    assert pr.registry_summary()["status"] == "ambiguous"
    with pytest.raises(ValueError, match="Ambiguous"):
        pr.resolve()
    assert pr.resolve(name="b")["profile"] == "b"


def test_override_is_task_only_and_hash_changes(project):
    root = project[0]
    before = (root / "config/reports/management.json").read_bytes()
    base = pr.resolve()
    changed = pr.resolve(overrides={"layout": {"columns": 1}})
    assert changed["sha256"] != base["sha256"]
    assert changed["settings"]["layout"]["columns"] == 1
    assert pr.resolve()["sha256"] == base["sha256"]
    assert (root / "config/reports/management.json").read_bytes() == before


def test_preferences_and_section_order_actually_apply(project):
    doc, shell = prepared(project)
    assert doc["charts"][0]["view"] == "bar"
    assert doc["charts"][0]["full_width"] is True
    assert shell.index('data-report-section="summary"') < shell.index('data-report-section="findings"')
    assert "repeat(2,minmax(0,1fr))" in shell
    assert "#146358" in shell
    assert "<caption>分析明细：核对金额" in shell
    assert "<!-- ECHART_CHART:rank -->" in shell


def test_real_report_delivery_and_immutable_source(project):
    from scripts.validate_delivery import validate_delivery
    root = project[0]
    before = (root / "results/amount.json").read_bytes()
    result = pr.build_report(root / "report.json", root / "report.html", root / "evidence.json")
    assert validate_delivery(result) == []
    content = result.read_text()
    assert '"view": "bar"' in content
    assert 'class="chart-card chart-card--wide"' in content
    assert 'id="project-report-contract"' in content
    assert (root / "results/amount.json").read_bytes() == before
    assert not (root / "config/reports/management.json.meta.json").exists()


@pytest.mark.parametrize("patch", [
    {"layout": {"columns": 3}}, {"charts": {"preferences": {"ranking": "pie"}}},
    {"charts": {"preferences": {"ranking": "bar"}, "avoid": ["bar"]}},
    {"analysis": {"run_shell": "anything"}}, {"disable_validation": True},
    {"layout": {"accent": "red;display:none"}}, {"layout": {"shell": "missing.html"}},
])
def test_invalid_preferences_never_silently_default(project, patch):
    with pytest.raises(ValueError):
        pr.resolve(overrides=patch)


def test_stale_profile_requires_replanning(project):
    root, profile, _, _ = project
    profile["layout"]["columns"] = 1
    write(root / "config/reports/management.json", profile)
    with pytest.raises(ValueError, match="changed since planning"):
        prepared(project)


def test_project_paths_and_symlink_escape_block(project, tmp_path):
    root = project[0]
    (tmp_path / "outside.html").write_text('<html><!-- REPORT_CONTENT --></html>')
    (root / "escape.html").symlink_to(tmp_path / "outside.html")
    for value in ("../outside.html", "escape.html"):
        with pytest.raises(ValueError, match="escapes"):
            pr.resolve(overrides={"layout": {"shell": value}})


@pytest.mark.parametrize("change,match", [
    ("method", "omits configured"), ("evidence", "unknown evidence"), ("section", "sections must match"),
    ("chart", "override reason"), ("query", "query evidence"), ("question", "omits project"),
])
def test_missing_or_conflicting_plan_is_blocking(project, change, match):
    doc = project[2]
    if change == "method":
        doc["report"]["methods"] = []
    elif change == "evidence":
        doc["report"]["methods"][0]["evidence_query_ids"] = ["invented"]
    elif change == "section":
        doc["report"]["sections"].pop()
    elif change == "chart":
        doc["charts"][0]["view"] = "column"
        doc["analysis_plan"]["views"][0].update(relation="magnitude", primary_view="column")
        # Force a contrary magnitude preference without changing the task hash.
        root, profile, _, _ = project
        profile["charts"]["preferences"]["magnitude"] = "bar"
        write(root / "config/reports/management.json", profile)
        doc["report"]["profile_sha256"] = pr.resolve()["sha256"]
    elif change == "query":
        doc["charts"][0]["query_hash"] = "wrong"
    elif change == "question":
        doc["analysis_plan"]["questions"] = ["Different question"]
    with pytest.raises(ValueError, match=match):
        prepared(project)


def test_data_gap_is_visible_not_false_execution(project):
    project[2]["report"]["methods"][0].update(status="data_gap", evidence_query_ids=[], note="缺少商品明细，无法完成该方法")
    _, shell = prepared(project)
    assert "数据缺口，未执行" in shell


def test_primary_table_appears_before_supporting_chart(project):
    project[2]["analysis_plan"]["views"][0]["table_mode"] = "primary"
    _, shell = prepared(project)
    assert shell.index("<caption>分析明细") < shell.index("<!-- ECHART_CHART:rank -->")


def test_custom_shell_and_notes_are_fingerprinted(project):
    root, profile, doc, _ = project
    shell = root / "templates/report.html"
    shell.parent.mkdir()
    shell.write_text('<html><head><style>body{background:#fff}</style></head><body><aside>项目品牌</aside><!-- REPORT_CONTENT --></body></html>')
    profile["layout"]["shell"] = "templates/report.html"
    profile["analysis"]["expert_notes"] = ["method.md"]
    (root / "method.md").write_text("按用户确认的分析方法解释结果。")
    write(root / "config/reports/management.json", profile)
    doc["report"]["profile_sha256"] = pr.resolve()["sha256"]
    assert "项目品牌" in prepared(project)[1]
    (root / "method.md").write_text("已修改的方法说明。")
    with pytest.raises(ValueError, match="changed since planning"):
        prepared(project)


def test_failed_delivery_preserves_previous_report(project, monkeypatch):
    root = project[0]
    output = root / "report.html"
    output.write_text("last verified report")
    monkeypatch.setattr("scripts.validate_delivery.validate_delivery", lambda *args, **kwargs: ["simulated browser failure"])
    with pytest.raises(ValueError, match="browser failure"):
        pr.build_report(root / "report.json", output, root / "evidence.json")
    assert output.read_text() == "last verified report"
    assert not list(root.glob("report-*.html"))


def test_legacy_report_engine_does_not_ignore_project_profile(project):
    from scripts.report_engine import ReportEngine
    with pytest.raises(ValueError, match="Project report profile detected"):
        ReportEngine(db_path=str(project[0] / "data.duckdb")).generate("anything")


def test_source_resolution_exposes_report_preferences(project):
    from scripts.project_data_context import resolve_sources
    assert resolve_sources("analysis", project[0])["project_report"]["default"] == "management"


def test_orphan_malformed_and_unknown_profile_block(project):
    root = project[0]
    with pytest.raises(ValueError, match="Unknown"):
        pr.resolve(name="missing")
    (root / pr.MANIFEST).unlink()
    with pytest.raises(ValueError, match="without manifest"):
        pr.resolve()
    (root / pr.MANIFEST).write_text('{"version":')
    assert pr.registry_summary()["status"] == "invalid"
    with pytest.raises(ValueError):
        pr.resolve()


def test_explicit_view_override_has_visible_reason(project):
    root, profile, doc, _ = project
    profile["charts"]["preferences"]["magnitude"] = "bar"
    write(root / "config/reports/management.json", profile)
    doc["report"]["profile_sha256"] = pr.resolve()["sha256"]
    doc["analysis_plan"]["views"][0].update(relation="magnitude", primary_view="column")
    doc["charts"][0].update(view="column", view_override_reason="本次明确要求使用纵向比较")
    prepared_doc, shell = prepared(project)
    assert prepared_doc["charts"][0]["view"] == "column"
    assert "本次明确要求使用纵向比较" in shell


@pytest.mark.parametrize("extra", [
    '<script>alert(1)</script>', '<img src="https://example.com/x">',
    '<meta http-equiv="refresh" content="0;url=https://example.com">',
    '<style>@import "https://example.com/a.css";</style>', '<p onclick="x()">x</p>',
])
def test_active_or_networked_shell_rejected_before_build(project, extra):
    root = project[0]
    (root / "shell.html").write_text('<html><head></head><body><!-- REPORT_CONTENT -->' + extra + '</body></html>')
    with pytest.raises(ValueError, match="passive"):
        pr.resolve(overrides={"layout": {"shell": "shell.html"}})


def test_missing_audit_metadata_does_not_replace_report(project):
    root = project[0]
    (root / "results/amount.json.meta.json").unlink()
    (root / "report.html").write_text("previous")
    with pytest.raises((ValueError, OSError)):
        pr.build_report(root / "report.json", root / "report.html", root / "evidence.json")
    assert (root / "report.html").read_text() == "previous"


def test_chart_cli_delegates_and_contract_rejects_tampering(project, monkeypatch):
    from scripts.chart_builder import main
    root = project[0]
    monkeypatch.setattr("sys.argv", ["chart_builder.py", str(root / "report.json"),
        "--output", str(root / "report.html"), "--evidence", str(root / "evidence.json")])
    assert main() is None
    output = root / "report.html"
    assert pr.validate_report_html(output) == []
    content = output.read_text()
    output.write_text(content.replace('data-report-section="summary"', 'data-report-section="wrong"'))
    assert any("sections differ" in e for e in pr.validate_report_html(output))
    output.write_text(content.replace('"profile_sha256": "', '"profile_sha256": "tampered'))
    assert any("hash mismatch" in e for e in pr.validate_report_html(output))


def test_multi_chart_report_and_uppercase_custom_shell(project):
    root, profile, doc, draft = project
    (root / "shell.html").write_text('<!doctype html><HTML lang="zh-CN"><HEAD><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Report</title></HEAD><BODY><!-- REPORT_CONTENT --></BODY></HTML>')
    profile["layout"]["shell"] = "shell.html"
    write(root / "config/reports/management.json", profile)
    doc["report"]["profile_sha256"] = pr.resolve()["sha256"]
    for identifier in ("detailA", "detailB"):
        chart = copy.deepcopy(doc["charts"][0])
        chart["id"] = identifier
        doc["charts"].append(chart)
        view = copy.deepcopy(doc["analysis_plan"]["views"][0])
        view.update(id=identifier, table_mode="source_toggle")
        doc["analysis_plan"]["views"].append(view)
    write(root / "report.json", doc)
    # The complete gate renders all three charts at desktop and mobile widths.
    result = pr.build_report(root / "report.json", root / "report.html", root / "evidence.json")
    assert result.read_text().count('class="chart-card chart-card--wide"') == 1


def test_skillhub_installed_report_build_uses_project_scheme(project, tmp_path):
    import os
    import subprocess
    import sys
    import zipfile
    from scripts.build_skill_package import build

    root = project[0]
    package = tmp_path / "distribution.zip"
    install = tmp_path / "installed-skill"
    build(pr.ROOT, package, "skillhub")
    with zipfile.ZipFile(package) as archive:
        archive.extractall(install)
    result = subprocess.run([sys.executable, str(install / "scripts/project_report.py"),
        "build", "report.json", "--evidence", "evidence.json", "--output", "report.html"],
        cwd=root, env=dict(os.environ, ECHART_PROJECT_ROOT=str(root)),
        capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert pr.validate_report_html(root / "report.html") == []
    assert "#146358" in (root / "report.html").read_text()
    assert not (install / "config/reports").exists()
