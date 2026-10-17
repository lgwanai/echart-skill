#!/usr/bin/env python3
"""Discover project report profiles and build evidence-bound reports from them.

Profiles describe analytical obligations, not executable plugins or canned
conclusions. The Agent runs the analysis through audited tools; this module
enforces coverage, applies layout/view preferences and validates before publish.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.project_cleaning import project_root, _inside, _read_json, _keys
from scripts.chart_capabilities import allowed_views
from scripts.chart_builder import SUPPORTED, json_script

MANIFEST = "config/reports/manifest.json"
CONTRACT_ID = "project-report-contract"
DEFAULT = {
    "version": 1, "audience": "业务决策者",
    "analysis": {"methods": [], "questions": [], "expert_notes": []},
    "layout": {"columns": 1, "accent": "#1d4ed8", "wide_charts": [],
               "sections": [{"id": "summary", "title": "结论摘要"},
                            {"id": "findings", "title": "关键发现"},
                            {"id": "actions", "title": "行动建议"}]},
    "charts": {"preferences": {}, "avoid": []},
}


def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()).hexdigest()


def _merge(base, patch):
    result = copy.deepcopy(base)
    for key, value in patch.items():
        result[key] = _merge(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else copy.deepcopy(value)
    return result


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be non-empty text")


def _texts(value, label, nonempty=False):
    if not isinstance(value, list) or nonempty and not value:
        raise ValueError(f"{label} must be a list")
    for item in value:
        _text(item, label)


def _id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", value):
        raise ValueError("IDs must start with a letter and contain only letters, digits, _ or -")


def _validate(profile, root, *, kind="report"):
    _keys(profile, DEFAULT, DEFAULT)
    if type(profile["version"]) is not int or profile["version"] != 1:
        raise ValueError("Unsupported report profile version")
    _text(profile["audience"], "audience")
    analysis = profile["analysis"]
    analysis_keys = {"methods", "questions", "expert_notes"}
    _keys(analysis, analysis_keys | ({"experts"} if kind == "dashboard" else set()), analysis_keys)
    _texts(analysis["questions"], "analysis.questions")
    _texts(analysis["expert_notes"], "analysis.expert_notes")
    if not isinstance(analysis["methods"], list):
        raise ValueError("analysis.methods must be a list")
    ids = set()
    for method in analysis["methods"]:
        _keys(method, {"id", "instructions"}, {"id", "instructions"})
        _id(method["id"])
        _text(method["instructions"], "method.instructions")
        if method["id"] in ids:
            raise ValueError("Duplicate method ID")
        ids.add(method["id"])
    for relative in analysis["expert_notes"]:
        path = _inside(root, relative)
        if path.suffix != ".md" or not path.is_file():
            raise ValueError("expert_notes must reference existing project Markdown files")
    layout = profile["layout"]
    _keys(layout, {"columns", "accent", "wide_charts", "sections", "shell"}, {"columns", "accent", "wide_charts", "sections"})
    columns = {1, 2, 3} if kind == "dashboard" else {1, 2}
    if type(layout["columns"]) is not int or layout["columns"] not in columns:
        raise ValueError(f"layout.columns must be one of {sorted(columns)}")
    if not isinstance(layout["accent"], str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", layout["accent"]):
        raise ValueError("accent must be a six-digit hex color")
    _texts(layout["wide_charts"], "wide_charts")
    for identifier in layout["wide_charts"]:
        _id(identifier)
    if not isinstance(layout["sections"], list) or not layout["sections"]:
        raise ValueError("layout.sections must be nonempty")
    ids = set()
    for section in layout["sections"]:
        _keys(section, {"id", "title"}, {"id", "title"})
        _id(section["id"])
        _text(section["title"], "section.title")
        if section["id"] in ids:
            raise ValueError("Duplicate section ID")
        ids.add(section["id"])
    if "shell" in layout:
        shell = _inside(root, layout["shell"])
        if not shell.is_file() or shell.suffix.lower() != ".html":
            raise ValueError("Report shell must be an existing project HTML file")
        content = shell.read_text(encoding="utf-8")
        marker = f"<!-- {kind.upper()}_CONTENT -->"
        if content.count(marker) != 1:
            raise ValueError(f"Custom {kind} shell needs exactly one {kind.upper()}_CONTENT marker")
        if any(len(re.findall(pattern, content, re.I)) != 1 for pattern in
               (r"<head\b[^>]*>", r"</head\s*>", r"<body\b[^>]*>", r"</body\s*>")):
            raise ValueError("Report shell needs one complete head and body")
        # Shells are presentation, not a route for arbitrary scripts/asset requests.
        if re.search(r"<\s*(script|iframe|object|embed|link|base)\b|\b(on\w+|src|srcset|href|http-equiv)\s*=|javascript:|@import|url\s*\(", content, re.I):
            raise ValueError("Report shell must be passive, self-contained HTML/CSS")
        if re.search(r"<!--\s*ECHART_CHART", content):
            raise ValueError("Report shell must not add compiler chart slots")
    charts = profile["charts"]
    _keys(charts, {"preferences", "avoid"}, {"preferences", "avoid"})
    if not isinstance(charts["preferences"], dict):
        raise ValueError("charts.preferences must be an object")
    _texts(charts["avoid"], "charts.avoid")
    if any(v not in SUPPORTED for v in charts["avoid"]):
        raise ValueError("Unknown avoided chart type")
    for relation, view in charts["preferences"].items():
        if view not in SUPPORTED or view not in allowed_views(relation):
            raise ValueError(f"Unsupported/inappropriate compiled preference: {relation} -> {view}")
        if view in charts["avoid"]:
            raise ValueError("A preferred chart cannot also be avoided")
    if kind == "dashboard":
        from scripts.project_dashboard import validate_experts
        validate_experts(profile, root)


def _manifest(kind):
    if kind not in {"report", "dashboard"}:
        raise ValueError("Unsupported project artifact kind")
    return f"config/{kind}s/manifest.json"


def _registry(root, *, kind="report"):
    path = _inside(root, _manifest(kind))
    if not path.exists():
        folder = path.parent
        if folder.exists() and any(folder.glob("*.json")):
            raise ValueError("Report JSON exists without manifest.json; register it before reporting")
        return None
    if root == ROOT:
        raise ValueError("Business report profiles belong to a user project, not the Skill")
    registry = _read_json(path)
    _keys(registry, {"version", "default", "profiles"}, {"version", "profiles"})
    if type(registry["version"]) is not int or registry["version"] != 1 or not isinstance(registry["profiles"], dict) or not registry["profiles"]:
        raise ValueError("Invalid report registry version/profiles")
    for name, relative in registry["profiles"].items():
        _id(name)
        if not _inside(root, relative).is_file():
            raise ValueError(f"Missing report profile: {name}")
    if "default" in registry and registry["default"] not in registry["profiles"]:
        raise ValueError("Report default references an unknown profile")
    return registry


def registry_summary(root=None, *, kind="report"):
    root = project_root(root)
    manifest = _manifest(kind)
    try:
        registry = _registry(root, kind=kind)
    except (ValueError, OSError) as exc:
        # Report-specific configuration must not block unrelated data discovery.
        return {"status": "invalid", "manifest": str(root / manifest), "error": str(exc)}
    if registry is None:
        return {"status": "not_configured", "manifest": str(root / manifest)}
    names = list(registry["profiles"])
    selected = registry.get("default") or (names[0] if len(names) == 1 else None)
    return {"status": "configured" if selected else "ambiguous", "profiles": names,
            "default": selected, "manifest": str(root / manifest),
            "instruction": f"Run project_{kind}.py resolve before {kind} planning; build with project_{kind}.py build."}


def resolve(root=None, name=None, overrides=None, *, kind="report"):
    root = project_root(root)
    registry = _registry(root, kind=kind)
    profile = copy.deepcopy(DEFAULT)
    if kind == "dashboard":
        profile["analysis"]["experts"] = []
        profile["layout"].update(columns=2, sections=[
            {"id": "overview", "title": "经营概览"}, {"id": "diagnostics", "title": "诊断与行动"}])
    selected = "builtin"
    if registry:
        names = list(registry["profiles"])
        selected = name or registry.get("default") or (names[0] if len(names) == 1 else None)
        if selected is None:
            raise ValueError("Ambiguous report profiles: select one or set the project default")
        if selected not in registry["profiles"]:
            raise ValueError("Unknown report profile")
        raw = _read_json(_inside(root, registry["profiles"][selected]))
        _keys(raw, DEFAULT)
        profile = _merge(profile, raw)
    elif name is not None:
        raise ValueError("No project report profiles are registered")
    if overrides is not None:
        _keys(overrides, {"audience", "analysis", "layout", "charts"})
        profile = _merge(profile, overrides)
    _validate(profile, root, kind=kind)
    assets = {}
    paths = profile["analysis"]["expert_notes"] + ([profile["layout"]["shell"]] if profile["layout"].get("shell") else [])
    paths += [e["path"] for e in profile["analysis"].get("experts", [])]
    for relative in paths:
        assets[relative] = hashlib.sha256(_inside(root, relative).read_bytes()).hexdigest()
    snapshot = {"profile": selected, "settings": profile, "assets": assets}
    if kind == "dashboard":
        snapshot["kind"] = kind
    return {"project_root": str(root), "status": "resolved", **snapshot, "sha256": _digest(snapshot)}


def _references(value, known, label, nonempty=True):
    _texts(value, label, nonempty)
    if not set(value) <= known:
        raise ValueError(f"{label} references unknown evidence")


def prepare(document, base, resolved, evidence, *, kind="report", evidence_base=None):
    """Validate analytical obligations and assemble a compiler-ready report shell."""
    from scripts.validate_analysis_plan import validate_plan
    from scripts.artifact_manifest import COMPARISON_BINDING_FIELDS

    document = copy.deepcopy(document)
    report = document.get(kind, {})
    body_keys = {"title", "scope", "limitations", "profile_sha256", "sections", "methods"}
    if kind == "dashboard":
        body_keys.add("kpis")
    _keys(report, body_keys, body_keys)
    for field in ("title", "scope"):
        _text(report[field], field)
    _texts(report["limitations"], "limitations", True)
    if report["profile_sha256"] != resolved["sha256"]:
        raise ValueError("Report profile changed since planning; resolve and re-plan before building")
    settings = resolved["settings"]
    plan = document.get("analysis_plan")
    if not isinstance(plan, dict):
        raise ValueError("A validated analysis_plan is required")
    if plan.get("audience") != settings["audience"]:
        raise ValueError("Analysis audience differs from the effective report profile")
    if not set(settings["analysis"]["questions"]) <= set(plan.get("questions", [])):
        raise ValueError("Analysis plan omits project report questions")
    known = {q["id"] for q in evidence["queries"]}
    # Validate all evidence before composing text or claims of execution.
    # materialized result_ref is relative to the eventual output, not spec base.
    method_specs = {m["id"]: m for m in settings["analysis"]["methods"]}
    if not isinstance(report["methods"], list):
        raise ValueError("report.methods must be a list")
    executions = {}
    for method in report["methods"]:
        _keys(method, {"id", "status", "evidence_query_ids", "note"}, {"id", "status", "evidence_query_ids", "note"})
        if method["id"] in executions or method["id"] not in method_specs:
            raise ValueError("Unknown/duplicate analysis method")
        _text(method["note"], "method note")
        if method["status"] not in {"executed", "data_gap"}:
            raise ValueError("Methods require executed or data_gap status")
        _references(method["evidence_query_ids"], known, "method evidence", method["status"] == "executed")
        executions[method["id"]] = method
    if set(executions) != set(method_specs):
        raise ValueError("Report omits configured analysis methods")
    section_specs = settings["layout"]["sections"]
    if not isinstance(report["sections"], list):
        raise ValueError("report.sections must be a list")
    sections = {}
    for section in report["sections"]:
        _keys(section, {"id", "paragraphs", "evidence_query_ids"}, {"id", "paragraphs", "evidence_query_ids"})
        if section["id"] in sections:
            raise ValueError("Duplicate report section")
        _texts(section["paragraphs"], "section paragraphs", True)
        _references(section["evidence_query_ids"], known, "section evidence")
        sections[section["id"]] = section
    if set(sections) != {s["id"] for s in section_specs}:
        raise ValueError("Report sections must match the effective layout")
    charts = document.get("charts")
    if not isinstance(charts, list) or not charts:
        raise ValueError("Compiled project reports currently require at least one supported chart")
    views = plan.get("views", [])
    if not isinstance(views, list) or not all(isinstance(v, dict) for v in views):
        raise ValueError("analysis_plan.views must be objects")
    view_map = {v.get("id"): v for v in views}
    if len(view_map) != len(views) or set(view_map) != {c.get("id") for c in charts} or len(charts) != len(view_map):
        raise ValueError("Planned view IDs and chart IDs must match exactly")
    choices = []
    for chart in charts:
        _id(chart.get("id"))
        if chart.get("section") not in sections:
            raise ValueError("Every chart requires a configured section")
        view_plan = view_map[chart["id"]]
        relation = view_plan.get("relation")
        preferred = settings["charts"]["preferences"].get(relation)
        chart.setdefault("view", preferred or view_plan.get("primary_view"))
        if chart["view"] != view_plan.get("primary_view"):
            raise ValueError("Chart type differs from the analysis plan")
        conflicting = (preferred and chart["view"] != preferred) or chart["view"] in settings["charts"]["avoid"]
        if conflicting:
            _text(chart.get("view_override_reason"), "Explicit task override reason")
        if chart["view"] not in SUPPORTED:
            raise ValueError("Specialized chart needs a separately verified implementation; no silent substitution")
        query = next((q for q in evidence["queries"] if q["id"] == view_plan.get("evidence_ref")), None)
        if query is None or query["query_hash"] != chart.get("query_hash"):
            raise ValueError("Chart/plan query evidence does not match")
        data = _read_json((base / chart["rows_path"]).resolve())
        if hashlib.sha256((base / chart["rows_path"]).read_bytes()).hexdigest() != query["result_sha256"]:
            raise ValueError("Chart data does not match its planned evidence")
        if view_plan.get("comparison") and not any(
            all(view_plan["comparison"].get(k, "calendar" if k == "calendar" else None) == c.get(k, "calendar" if k == "calendar" else None)
                for k in COMPARISON_BINDING_FIELDS) for c in evidence.get("comparisons", [])
        ):
            raise ValueError("Planned comparison windows are not bound to the actual evidence")
        # Validate actual density, not only the Agent's declared row/measure counts.
        view_plan["category_count"] = len(data)
        view_plan["measure_count"] = len(chart.get("metrics", []))
        chart["full_width"] = chart["id"] in settings["layout"]["wide_charts"]
        choices.append({"id": chart["id"], "relation": relation, "view": chart["view"],
                        "override_reason": chart.get("view_override_reason", "")})
    if not set(settings["layout"]["wide_charts"]) <= set(view_map):
        raise ValueError("wide_charts references missing chart IDs")
    errors = validate_plan(plan)
    if errors:
        raise ValueError("; ".join(errors))
    manifest_findings = {f.get("id"): f for f in evidence.get("findings", [])}
    for finding in plan["findings"]:
        _references(finding["evidence_refs"], known, "finding evidence")
        bound = manifest_findings.get(finding["id"])
        if not bound or set(bound.get("evidence_query_ids", [])) != set(finding["evidence_refs"]) or bound.get("why_status") != finding["why_status"]:
            raise ValueError("Plan findings must be bound in the evidence manifest")
    if kind == "dashboard":
        from scripts.project_dashboard import render_dashboard
        return document, render_dashboard(document, base, resolved, evidence, choices, evidence_base or base)
    esc = lambda value: html.escape(str(value), quote=True)
    content = [f'<main class="project-report"><header><h1>{esc(report["title"])}</h1><p>统计口径：{esc(report["scope"])}</p><p>阅读对象：{esc(settings["audience"])}</p></header>']
    for section_spec in section_specs:
        identifier = section_spec["id"]
        section = sections[identifier]
        content.append(f'<section data-report-section="{identifier}"><h2>{esc(section_spec["title"])}</h2>')
        content.extend(f'<p>{esc(p)}</p>' for p in section["paragraphs"])
        content.append(f'<p>数据引用：{esc(", ".join(section["evidence_query_ids"]))}</p><div class="report-chart-grid">')
        for chart in charts:
            if chart["section"] != identifier:
                continue
            chart_position = len(content)
            content.append(f'<!-- ECHART_CHART:{chart["id"]} -->')
            if chart.get("view_override_reason"):
                content.append(f'<p class="report-wide">图表选择说明：{esc(chart["view_override_reason"])}</p>')
            vp = view_map[chart["id"]]
            if vp["table_mode"] in {"companion", "primary"}:
                table_position = len(content)
                columns = vp["table_columns"]
                rows = _read_json(base / chart["rows_path"])
                if any(c not in row for row in rows for c in columns):
                    raise ValueError("Companion table columns missing from actual query result")
                content.append('<div class="table-scroll report-wide"><table><caption>分析明细：' + esc(vp["table_reason"]) + '</caption><thead><tr>')
                content.extend(f'<th>{esc(c)}</th>' for c in columns)
                content.append('</tr></thead><tbody>')
                for row in rows:
                    content.append('<tr>' + ''.join(f'<td>{esc(row[c]) if row[c] is not None else "—"}</td>' for c in columns) + '</tr>')
                content.append('</tbody></table></div>')
                if vp["table_mode"] == "primary":
                    table_content = content[table_position:]
                    del content[table_position:]
                    content[chart_position:chart_position] = table_content
        content.append('</div></section>')
    content.append('<section><h2>分析方法与限制</h2>')
    for method in settings["analysis"]["methods"]:
        execution = executions[method["id"]]
        label = "已执行" if execution["status"] == "executed" else "数据缺口，未执行"
        content.append(f'<p>{esc(method["id"])}（{label}）：{esc(execution["note"])}；数据引用：{esc(", ".join(execution["evidence_query_ids"]))}</p>')
    content.extend(f'<p>{esc(limit)}</p>' for limit in report["limitations"])
    content.append('<h2>数据来源与审计</h2>')
    content.extend(f'<p>{esc(q["id"])} · query hash: {esc(q["query_hash"])} · 记录数：{q["row_count"]}</p>' for q in evidence["queries"])
    content.append('</section></main>')
    shell_path = settings["layout"].get("shell")
    shell = _inside(Path(resolved["project_root"]), shell_path).read_text(encoding="utf-8") if shell_path else '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>分析报告</title></head><body><!-- REPORT_CONTENT --></body></html>'
    shell = shell.replace('<!-- REPORT_CONTENT -->', ''.join(content))
    columns, accent = settings["layout"]["columns"], settings["layout"]["accent"]
    css = f'''<style>
    body .project-report{{max-width:1160px;background:white;padding:32px;margin:24px auto;box-sizing:border-box}}
    .project-report h1,.project-report h2{{color:{accent}}}
    .project-report .report-chart-grid{{display:grid;grid-template-columns:repeat({columns},minmax(0,1fr));gap:18px}}
    .project-report .chart-card--wide,.project-report .report-wide{{grid-column:1/-1}}
    .project-report section{{min-width:0}} .project-report p{{overflow-wrap:anywhere}}
    @media(max-width:760px){{body .project-report{{padding:16px;margin:0}}.project-report .report-chart-grid{{grid-template-columns:minmax(0,1fr)}}}}
    @media print{{body{{background:white}}body .project-report{{margin:0;max-width:none}}.chart-card{{break-inside:avoid}}}}
    </style>'''
    shell = re.sub(r'</head\s*>', lambda _: css + '</head>', shell, flags=re.I)
    contract = {"version": 1, "snapshot": {k: resolved[k] for k in ("profile", "settings", "assets")},
                "profile_sha256": resolved["sha256"], "methods": report["methods"], "chart_choices": choices}
    shell = re.sub(r'</body\s*>', lambda _: f'<script id="{CONTRACT_ID}" type="application/json">{json_script(contract)}</script></body>', shell, flags=re.I)
    comparisons = evidence.get("comparisons", [])
    if comparisons:
        shell = shell.replace('</body>', f'<script id="analysis-comparison-contract" type="application/json">{json_script({"version": 1, "comparisons": comparisons})}</script></body>')
    return document, shell


def validate_report_html(path, *, kind="report"):
    from html.parser import HTMLParser
    from scripts.artifact_manifest import _extract_json_script, MANIFEST_ID

    content = Path(path).read_text(encoding="utf-8")
    contract_id = f"project-{kind}-contract"
    if contract_id not in content and f'data-project-{kind}' not in content and f'class="project-{kind}"' not in content:
        return []
    contract, errors = _extract_json_script(content, contract_id)
    if errors:
        return errors
    try:
        if contract.get("version") != 1 or _digest(contract["snapshot"]) != contract["profile_sha256"]:
            raise ValueError("Report profile snapshot/hash mismatch")
        if kind == "dashboard" and contract["snapshot"].get("kind") != "dashboard":
            raise ValueError("Dashboard profile kind mismatch")
        settings = contract["snapshot"]["settings"]
        class Sections(HTMLParser):
            def __init__(self):
                super().__init__()
                self.ids = []
            def handle_starttag(self, tag, attrs):
                if f"data-{kind}-section" in dict(attrs):
                    self.ids.append(dict(attrs)[f"data-{kind}-section"])
        sections = Sections()
        sections.feed(content)
        if sections.ids != [s["id"] for s in settings["layout"]["sections"]]:
            raise ValueError("Report sections differ from the project layout/order")
        match = re.search(r'<script id="chart-build-spec" type="application/json">(.*?)</script>', content, re.S)
        configs = json.loads(match[1]) if match else []
        choices = contract["chart_choices"]
        if len(configs) != len(choices) or {c["id"] for c in configs} != {c["id"] for c in choices}:
            raise ValueError("Report chart coverage mismatch")
        for compiled in configs:
            choice = next(c for c in choices if c["id"] == compiled["id"])
            if choice["view"] != compiled["input"]["view"]:
                raise ValueError("Rendered chart differs from report choice")
            preferred = settings["charts"]["preferences"].get(choice["relation"])
            if ((preferred and choice["view"] != preferred) or choice["view"] in settings["charts"]["avoid"]) and not choice["override_reason"].strip():
                raise ValueError("Unexplained report chart preference override")
        manifest, manifest_errors = _extract_json_script(content, MANIFEST_ID)
        if manifest_errors:
            return manifest_errors
        known = {q["id"] for q in manifest["queries"]}
        methods = contract["methods"]
        required = {m["id"] for m in settings["analysis"]["methods"]}
        if len(methods) != len(required) or {m["id"] for m in methods} != required:
            raise ValueError("Report method coverage mismatch")
        for method in methods:
            if method["status"] not in {"executed", "data_gap"}:
                raise ValueError("Invalid method execution status")
            _references(method["evidence_query_ids"], known, "method evidence", method["status"] == "executed")
            _text(method["note"], "method note")
        if kind == "dashboard":
            from scripts.project_dashboard import validate_dashboard_contract
            validate_dashboard_contract(path, content, contract, manifest, configs)
    except (ValueError, KeyError, TypeError, StopIteration) as exc:
        errors.append(f"Project report contract: {exc}")
    return errors


def build_report(spec_path, output, evidence_path, *, root=None, name=None, overrides=None, kind="report"):
    from scripts.artifact_manifest import materialize_manifest, embed_manifest, validate_manifest
    from scripts.chart_builder import build_html
    from scripts.validate_delivery import validate_delivery

    spec_path, output, evidence_path = map(lambda p: Path(p).resolve(), (spec_path, output, evidence_path))
    resolved = resolve(root, name, overrides, kind=kind)
    draft = _read_json(evidence_path)
    evidence = materialize_manifest(draft, evidence_path, output)
    errors = validate_manifest(evidence, output)
    if errors:
        raise ValueError("; ".join(errors))
    for query in evidence["queries"]:
        result = (output.parent / query["result_ref"]).resolve()
        meta = _read_json(Path(str(result) + ".meta.json"))
        if meta.get("query_hash") != query["query_hash"] or meta.get("lineage_recorded") is not True:
            raise ValueError("Report methods require audited query-result metadata")
    document, shell = prepare(_read_json(spec_path), spec_path.parent, resolved, evidence, kind=kind, evidence_base=output.parent)
    content = build_html(document, spec_path.parent, shell, output.parent)
    if kind == "dashboard":
        from scripts.project_dashboard import add_runtime
        content = add_runtime(content)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=output.parent, prefix=output.stem + "-", suffix=".html")
    os.close(fd)
    candidate = Path(temporary)
    try:
        candidate.write_text(content, encoding="utf-8")
        embed_manifest(candidate, evidence)
        errors = validate_delivery(candidate)
        if errors:
            raise ValueError("; ".join(errors))
        candidate.replace(output)
    finally:
        candidate.unlink(missing_ok=True)
    return output


def main(argv=None, *, kind="report"):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root")
    parser.add_argument("--profile")
    parser.add_argument("--overrides", type=Path, help="Task-only preference overrides; never saved to the registry")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("resolve")
    build = commands.add_parser("build")
    build.add_argument("spec", type=Path)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        overrides = _read_json(args.overrides) if args.overrides else None
        if args.command == "resolve":
            print(json.dumps(resolve(args.project_root, args.profile, overrides, kind=kind), ensure_ascii=False, indent=2))
        else:
            output = build_report(args.spec, args.output, args.evidence, root=args.project_root, name=args.profile, overrides=overrides, kind=kind)
            print(f"Verified project {kind}: {output}")
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"{kind.title()} rejected: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
