import copy
import json
import os
import subprocess
import sys
import zipfile

import pytest

from scripts import project_dashboard as pd
from scripts import project_report as pr
from scripts.artifact_manifest import materialize_manifest
from tests.test_project_report import project as report_project, write


@pytest.fixture
def project(report_project):
    root, original, report, evidence = report_project
    profile = copy.deepcopy(original)
    profile["audience"] = "经营运营团队"
    profile["analysis"]["experts"] = [{"id": "operations", "path": "experts/operations.md", "role": "primary", "method_ids": ["ranking"]}]
    (root / "experts").mkdir()
    (root / "experts/operations.md").write_text("# 项目经营专家\n分析区域金额排名，核对集中度；无时间字段时说明无法诊断趋势。")
    write(root / "config/dashboards/operations.json", profile)
    write(root / pd.MANIFEST, {"version": 1, "default": "operations", "profiles": {"operations": "config/dashboards/operations.json"}})
    doc = copy.deepcopy(report)
    doc["artifact_type"] = "dashboard"
    doc["dashboard"] = doc.pop("report")
    doc["dashboard"]["title"] = "区域经营 Dashboard"
    doc["dashboard"]["limitations"] = ["只有两条区域汇总记录，无时间、品类及成本字段，趋势、交叉分析和原因归因无法执行。"]
    doc["dashboard"]["profile_sha256"] = pd.resolve()["sha256"]
    doc["dashboard"]["kpis"] = [{"id": "north", "label": "North金额", "unit": "元", "scope": "North区域金额", "query_id": "q1", "row": 0, "field": "amount"}]
    doc["analysis_plan"]["audience"] = profile["audience"]
    write(root / "dashboard.json", doc)
    return root, profile, doc, evidence


def prepare(project, overrides=None):
    root, _, doc, draft = project
    evidence = materialize_manifest(draft, root / "evidence.json", root / "dashboard.html")
    return pr.prepare(doc, root, pd.resolve(overrides=overrides), evidence, kind="dashboard")


def test_discovery_separate_from_report_and_other_projects(project, monkeypatch, tmp_path):
    root = project[0]
    nested = root / "outputs/deep"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    resolved = pd.resolve()
    assert resolved["project_root"] == str(root)
    assert resolved["profile"] == "operations"
    assert resolved["settings"]["analysis"]["experts"][0]["role"] == "primary"
    assert pr.resolve()["profile"] == "management"
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(other)
    assert pd.resolve()["profile"] == "builtin"
    assert not (other / "config").exists()
    monkeypatch.setenv("ECHART_PROJECT_ROOT", str(root))
    assert pd.resolve()["profile"] == "operations"


def test_dashboard_directory_alone_marks_project_root(tmp_path, monkeypatch):
    (tmp_path / "config/dashboards").mkdir(parents=True)
    (tmp_path / "nested").mkdir()
    monkeypatch.chdir(tmp_path / "nested")
    monkeypatch.delenv("ECHART_PROJECT_ROOT", raising=False)
    assert pd.resolve()["project_root"] == str(tmp_path.resolve())


def test_default_selection_ambiguity_and_task_override(project):
    root, _, _, _ = project
    before = (root / "config/dashboards/operations.json").read_bytes()
    base = pd.resolve()
    temporary = pd.resolve(overrides={"layout": {"columns": 3}})
    assert temporary["settings"]["layout"]["columns"] == 3
    assert base["sha256"] != temporary["sha256"]
    assert (root / "config/dashboards/operations.json").read_bytes() == before
    write(root / pd.MANIFEST, {"version": 1, "profiles": {"a": "config/dashboards/operations.json", "b": "config/dashboards/operations.json"}})
    with pytest.raises(ValueError, match="Ambiguous"):
        pd.resolve()
    assert pd.resolve(name="b")["profile"] == "b"
    assert pd.registry_summary()["status"] == "ambiguous"


@pytest.mark.parametrize("change", ["expert", "layout", "shell"])
def test_changed_project_assets_invalidate_plan(project, change):
    root, profile, _, _ = project
    if change == "expert":
        (root / "experts/operations.md").write_text("New analytical obligations")
    elif change == "layout":
        profile["layout"]["columns"] = 3
        write(root / "config/dashboards/operations.json", profile)
    else:
        (root / "shell.html").write_text('<html><head></head><body><!-- DASHBOARD_CONTENT --></body></html>')
        profile["layout"]["shell"] = "shell.html"
        write(root / "config/dashboards/operations.json", profile)
    with pytest.raises(ValueError, match="changed since planning"):
        prepare(project)


@pytest.mark.parametrize("patch", [
    {"layout": {"columns": 4}}, {"layout": {"accent": "red;display:none"}},
    {"charts": {"preferences": {"ranking": "pie"}}}, {"analysis": {"execute": "command"}},
    {"analysis": {"experts": [{"id": "a", "path": "experts/operations.md", "role": "supporting", "method_ids": ["ranking"]}]}},
    {"analysis": {"experts": [{"id": "a", "path": "experts/operations.md", "role": "primary", "method_ids": ["unknown"]}]}},
    {"analysis": {"experts": [{"id": "a", "path": "../escape.md", "role": "primary", "method_ids": ["ranking"]}]}},
])
def test_invalid_profile_blocks_instead_of_falling_back(project, patch):
    with pytest.raises(ValueError):
        pd.resolve(overrides=patch)


def test_source_resolver_reports_dashboard_registry(project):
    from scripts.project_data_context import resolve_sources
    assert resolve_sources("经营看板", project[0])["project_dashboard"]["default"] == "operations"


def test_methods_and_actual_kpi_are_enforced(project):
    doc, shell = prepare(project)
    assert doc["charts"][0]["view"] == "bar"
    assert 'data-kpi-value="north">20</strong>' in shell
    assert "主专家：operations" in shell
    assert shell.index('data-dashboard-section="summary"') < shell.index('data-dashboard-section="findings"')
    assert "<caption>核对金额" in shell
    project[2]["dashboard"]["methods"] = []
    with pytest.raises(ValueError, match="omits configured"):
        prepare(project)


@pytest.mark.parametrize("patch", [{"value": 999}, {"row": -1}, {"field": "missing"}, {"query_id": "unknown"}])
def test_kpi_cannot_be_hand_entered_or_unbound(project, patch):
    project[2]["dashboard"]["kpis"][0].update(patch)
    with pytest.raises(ValueError):
        prepare(project)


def test_visible_method_gap(project):
    project[2]["dashboard"]["methods"][0].update(status="data_gap", evidence_query_ids=[], note="缺少品类字段，无法深入验证")
    assert "数据缺口，未执行" in prepare(project)[1]


def test_real_browser_build_and_static_contract_tamper(project):
    from scripts.validate_delivery import validate_delivery
    root = project[0]
    before = (root / "results/amount.json").read_bytes()
    output = pd.build_dashboard(root / "dashboard.json", root / "outputs/dashboard.html", root / "evidence.json")
    assert validate_delivery(output) == []
    assert (root / "results/amount.json").read_bytes() == before
    content = output.read_text()
    output.write_text(content.replace('data-kpi-value="north">20</strong>', 'data-kpi-value="north">999</strong>'))
    assert any("KPI" in e for e in pr.validate_report_html(output, kind="dashboard"))


def test_missing_evidence_and_browser_failure_preserve_previous_output(project, monkeypatch):
    root = project[0]
    output = root / "dashboard.html"
    output.write_text("previous verified dashboard")
    monkeypatch.setattr("scripts.validate_delivery.validate_delivery", lambda *a, **k: ["simulated browser failure"])
    with pytest.raises(ValueError, match="browser failure"):
        pd.build_dashboard(root / "dashboard.json", output, root / "evidence.json")
    assert output.read_text() == "previous verified dashboard"
    assert not list(root.glob("dashboard-*.html"))
    (root / "results/amount.json.meta.json").unlink()
    with pytest.raises(ValueError):
        pd.build_dashboard(root / "dashboard.json", output, root / "evidence.json")
    assert output.read_text() == "previous verified dashboard"


def test_layout_promotes_incomplete_rows_without_changing_profile(project):
    _, profile, doc, _ = project
    doc["analysis_plan"]["views"][0]["table_mode"] = "source_toggle"
    for i in range(1, 4):
        chart = copy.deepcopy(doc["charts"][0])
        view = copy.deepcopy(doc["analysis_plan"]["views"][0])
        chart["id"] = view["id"] = f"detail{i}"
        doc["charts"].append(chart)
        doc["analysis_plan"]["views"].append(view)
    result, _ = prepare(project)
    assert [c["full_width"] for c in result["charts"]] == [True, False, False, True]
    assert profile["layout"]["wide_charts"] == ["rank"]


def test_chart_builder_routes_dashboard_and_blocks_legacy_bypass(project, monkeypatch):
    from scripts.chart_builder import main
    root = project[0]
    monkeypatch.setattr(sys, "argv", ["chart_builder.py", "dashboard.json", "--output", "dashboard.html", "--evidence", "evidence.json"])
    main()
    assert (root / "dashboard.html").is_file()
    write(root / "legacy.json", {"charts": project[2]["charts"]})
    (root / "legacy.html").write_text('<html><head></head><body><div class="dashboard-grid"><!-- ECHART_CHARTS --></div></body></html>')
    monkeypatch.setattr(sys, "argv", ["chart_builder.py", "legacy.json", "--output", "bypass.html", "--shell", "legacy.html"])
    with pytest.raises(SystemExit):
        main()
    assert not (root / "bypass.html").exists()


def test_installed_skillhub_build(project, tmp_path):
    from scripts.build_skill_package import build
    from scripts.validate_release_package import validate_package
    root = project[0]
    archive_path = tmp_path / "skillhub.zip"
    build(pd.ROOT, archive_path, "skillhub")
    assert validate_package(archive_path, "skillhub") == []
    install = tmp_path / "installed-skill"
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(install)
    result = subprocess.run([sys.executable, str(install / "scripts/project_dashboard.py"),
        "build", "dashboard.json", "--evidence", "evidence.json", "--output", "installed.html"],
        cwd=root, env=dict(os.environ, ECHART_PROJECT_ROOT=str(root)), capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert pr.validate_report_html(root / "installed.html", kind="dashboard") == []
    assert not (install / "config/dashboards").exists()


def test_expert_symlink_escape_and_orphan_registry(project, tmp_path):
    root, profile, _, _ = project
    (tmp_path / "outside.md").write_text("External notes")
    (root / "experts/link.md").symlink_to(tmp_path / "outside.md")
    profile["analysis"]["experts"][0]["path"] = "experts/link.md"
    write(root / "config/dashboards/operations.json", profile)
    with pytest.raises(ValueError, match="escapes"):
        pd.resolve()
    (root / pd.MANIFEST).unlink()
    with pytest.raises(ValueError, match="without manifest"):
        pd.resolve()


@pytest.mark.parametrize("columns", [2, 3])
def test_multicolumn_layout_and_real_controls(project, columns):
    from scripts.browser_smoke_test import find_playwright_runtime
    root, profile, doc, _ = project
    profile["layout"]["columns"] = columns
    write(root / "config/dashboards/operations.json", profile)
    doc["dashboard"]["profile_sha256"] = pd.resolve()["sha256"]
    doc["analysis_plan"]["views"][0]["table_mode"] = "source_toggle"
    for i in range(columns):
        chart, view = copy.deepcopy(doc["charts"][0]), copy.deepcopy(doc["analysis_plan"]["views"][0])
        chart["id"] = view["id"] = f"detail{i}"
        doc["charts"].append(chart)
        doc["analysis_plan"]["views"].append(view)
    write(root / "dashboard.json", doc)
    output = pd.build_dashboard(root / "dashboard.json", root / "dashboard.html", root / "evidence.json")
    runtime = find_playwright_runtime()
    assert runtime is not None
    node, modules, browser = runtime
    env = dict(os.environ)
    if modules:
        env["NODE_PATH"] = str(modules)
    script = r'''
const {chromium}=require('playwright'), fs=require('fs'), {pathToFileURL}=require('url');
(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:process.argv[1]});
  try {
    const page=await browser.newPage({viewport:{width:1440,height:1000}});
    await page.goto(pathToFileURL(process.argv[2]).href);
    const summary=page.locator('details[data-chart-table="rank"] summary');
    await summary.click();
    if (!await page.locator('details[data-chart-table="rank"] table').isVisible()) throw Error('Source table stays hidden');
    await summary.click();
    const svgPromise=page.waitForEvent('download');
    await page.locator('[data-download-chart="rank"]').click();
    const svg=await svgPromise;
    if (!fs.readFileSync(await svg.path(),'utf8').includes('<svg')) throw Error('Downloaded chart is not SVG');
    const pdfPromise=page.waitForEvent('download',{timeout:20000});
    await page.locator('#export-dashboard').click();
    const pdf=await pdfPromise;
    if (fs.readFileSync(await pdf.path()).subarray(0,4).toString()!=='%PDF') throw Error('Export is not a real PDF');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
'''
    result = subprocess.run([str(node), "-e", script, str(browser), str(output)], env=env, capture_output=True, text=True, timeout=40)
    assert result.returncode == 0, result.stdout + result.stderr


def test_custom_shell_cannot_hide_kpis_or_override_grid(project):
    root, profile, doc, _ = project
    (root / "shell.html").write_text('<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>[data-kpi-value]{display:none}</style></head><body><!-- DASHBOARD_CONTENT --></body></html>')
    profile["layout"]["shell"] = "shell.html"
    write(root / "config/dashboards/operations.json", profile)
    doc["dashboard"]["profile_sha256"] = pd.resolve()["sha256"]
    write(root / "dashboard.json", doc)
    output = root / "dashboard.html"
    output.write_text("last verified")
    with pytest.raises(ValueError, match="hidden"):
        pd.build_dashboard(root / "dashboard.json", output, root / "evidence.json")
    assert output.read_text() == "last verified"


def test_kpi_fractional_value_is_not_rounded_or_coerced(project):
    from scripts.sql_runner import main
    root, _, doc, draft = project
    main(["--db", str(root / "data.duckdb"), "--sql", "SELECT CAST(20.125 AS DOUBLE) amount",
          "--output", "json", "--out", str(root / "results/kpi.json")])
    meta = json.loads((root / "results/kpi.json.meta.json").read_text())
    draft["queries"].append({"id": "kpi", "result_path": "results/kpi.json", "query_hash": meta["query_hash"]})
    doc["dashboard"]["kpis"][0]["query_id"] = "kpi"
    write(root / "evidence.json", draft)
    write(root / "dashboard.json", doc)
    output = pd.build_dashboard(root / "dashboard.json", root / "dashboard.html", root / "evidence.json")
    assert 'data-kpi-value="north">20.125</strong>' in output.read_text()
