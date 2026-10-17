#!/usr/bin/env python3
"""Project-owned Dashboard experts/preferences, evidence-bound assembly and reuse.

Shares registry and analytical gates with project_report; no project code runs.
The Agent chooses/executes the analysis. This module deterministically applies
the resulting plan, loads actual KPI values, and publishes only verified HTML.
"""
from __future__ import annotations

import html
import math
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import project_report as shared
from scripts.project_cleaning import _inside, _keys, _read_json
from scripts.chart_builder import json_script

MANIFEST = "config/dashboards/manifest.json"
CONTRACT_ID = "project-dashboard-contract"
esc = lambda value: html.escape(str(value), quote=True)


def resolve(root=None, name=None, overrides=None):
    return shared.resolve(root, name, overrides, kind="dashboard")


def registry_summary(root=None):
    return shared.registry_summary(root, kind="dashboard")


def build_dashboard(spec_path, output, evidence_path, **kwargs):
    return shared.build_report(spec_path, output, evidence_path, kind="dashboard", **kwargs)


def validate_experts(profile, root):
    experts = profile["analysis"].get("experts", [])
    if not isinstance(experts, list):
        raise ValueError("analysis.experts must be a list")
    known = {m["id"] for m in profile["analysis"]["methods"]}
    ids, primary = set(), 0
    for expert in experts:
        _keys(expert, {"id", "path", "role", "method_ids"}, {"id", "path", "role", "method_ids"})
        shared._id(expert["id"])
        if expert["id"] in ids:
            raise ValueError("Duplicate project expert ID")
        ids.add(expert["id"])
        if expert["role"] not in {"primary", "supporting"}:
            raise ValueError("Expert role must be primary or supporting")
        primary += expert["role"] == "primary"
        path = _inside(root, expert["path"])
        if path.suffix != ".md" or not path.is_file() or not path.read_text(encoding="utf-8").strip():
            raise ValueError("Project experts require nonempty project Markdown files")
        shared._references(expert["method_ids"], known, "expert method_ids")
    if experts and primary != 1:
        raise ValueError("Project experts require exactly one primary expert")


def load_kpis(specs, evidence, evidence_base):
    if not isinstance(specs, list) or not specs:
        raise ValueError("Dashboard requires at least one evidence-bound KPI")
    result, ids = [], set()
    fields = {"id", "label", "unit", "scope", "query_id", "row", "field"}
    queries = {q["id"]: q for q in evidence["queries"]}
    for spec in specs:
        _keys(spec, fields, fields)
        shared._id(spec["id"])
        if spec["id"] in ids:
            raise ValueError("Duplicate KPI ID")
        ids.add(spec["id"])
        for key in ("label", "unit", "scope", "query_id", "field"):
            shared._text(spec[key], f"KPI {key}")
        query = queries.get(spec["query_id"])
        if query is None:
            raise ValueError("KPI references unknown evidence query")
        rows = _read_json((evidence_base / query["result_ref"]).resolve())
        index = spec["row"]
        if type(index) is not int or not isinstance(rows, list) or not 0 <= index < len(rows):
            raise ValueError("KPI row is outside the actual query result")
        if not isinstance(rows[index], dict) or spec["field"] not in rows[index]:
            raise ValueError("KPI field missing from query result")
        value = rows[index][spec["field"]]
        if type(value) not in {int, float} or abs(value) > 2**53 - 1 or not math.isfinite(value):
            raise ValueError("KPI value must be a finite JS-safe number; do not fill missing data with zero")
        result.append({**spec, "value": value, "query_hash": query["query_hash"]})
    return result


def apply_spans(charts, settings, views):
    """Promote only; retain requested wide cards and prevent incomplete grid rows."""
    columns = settings["layout"]["columns"]
    for section in settings["layout"]["sections"]:
        group = [c for c in charts if c["section"] == section["id"]]
        run = []
        def flush():
            remainder = len(run) % columns
            for c in run[-remainder:] if remainder else []:
                c["full_width"] = True
            run.clear()
        for index, chart in enumerate(group):
            chart["full_width"] = bool(chart["full_width"] or index == 0 or
                chart["view"] in {"line", "area", "stacked_area", "mixed"} or
                views[chart["id"]]["table_mode"] != "source_toggle")
            if chart["full_width"]:
                flush()
            else:
                run.append(chart)
        flush()


def render_dashboard(document, base, resolved, evidence, choices, evidence_base):
    body, settings = document["dashboard"], resolved["settings"]
    views = {v["id"]: v for v in document["analysis_plan"]["views"]}
    charts = document["charts"]
    apply_spans(charts, settings, views)
    kpis = load_kpis(body["kpis"], evidence, evidence_base)
    sections = {s["id"]: s for s in body["sections"]}
    content = [f'<main class="dashboard-container" data-project-dashboard="1"><header class="dashboard-header"><h1>{esc(body["title"])}</h1><p>统计口径：{esc(body["scope"])}</p><p>阅读对象：{esc(settings["audience"])}</p></header>',
               '<div class="dashboard-toolbar"><button id="export-dashboard" type="button">导出 PDF</button><span>离线数据快照；更新数据后重新生成</span></div><div class="kpi-grid">']
    for kpi in kpis:
        content.append(f'<article class="kpi-card"><h2>{esc(kpi["label"])}</h2><strong data-kpi-value="{kpi["id"]}">{esc(kpi["value"])}</strong> <span>{esc(kpi["unit"])}</span><p>统计口径：{esc(kpi["scope"])}</p><p>数据来源：{esc(kpi["query_id"])} · query hash: {esc(kpi["query_hash"])}</p></article>')
    content.append('</div><div class="dashboard-grid">')
    for section in settings["layout"]["sections"]:
        item = sections[section["id"]]
        content.append(f'<section class="dashboard-wide insight-card" data-dashboard-section="{section["id"]}"><h2>{esc(section["title"])}</h2>')
        content.extend(f'<p>{esc(p)}</p>' for p in item["paragraphs"])
        content.append(f'<p>数据引用：{esc(", ".join(item["evidence_query_ids"]))}</p></section>')
        for chart in charts:
            if chart["section"] != section["id"]:
                continue
            view = views[chart["id"]]
            table = ""
            if view["table_mode"] in {"companion", "primary"}:
                columns = view["table_columns"]
                rows = _read_json(base / chart["rows_path"])
                if any(column not in row for column in columns for row in rows):
                    raise ValueError("Companion table column missing from query result")
                table = '<div class="table-scroll dashboard-wide"><table><caption>' + esc(view["table_reason"]) + '</caption><thead><tr>'
                table += ''.join(f'<th>{esc(c)}</th>' for c in columns) + '</tr></thead><tbody>'
                table += ''.join('<tr>' + ''.join(f'<td>{esc(row[c]) if row[c] is not None else "—"}</td>' for c in columns) + '</tr>' for row in rows)
                table += '</tbody></table></div>'
            if view["table_mode"] == "primary":
                content.append(table)
            content.append(f'<!-- ECHART_CHART:{chart["id"]} -->')
            if view["table_mode"] == "companion":
                content.append(table)
            if chart.get("view_override_reason"):
                content.append(f'<p class="dashboard-wide">图表选择说明：{esc(chart["view_override_reason"])}</p>')
    content.append('</div><section class="diagnostic-panel"><h2>项目专家、分析方法与限制</h2>')
    for expert in settings["analysis"]["experts"]:
        role = "主专家" if expert["role"] == "primary" else "辅助专家"
        content.append(f'<p>{role}：{esc(expert["id"])}；方法：{esc(", ".join(expert["method_ids"]))}</p>')
    for method in body["methods"]:
        label = "已执行" if method["status"] == "executed" else "数据缺口，未执行"
        content.append(f'<p>{esc(method["id"])}（{label}）：{esc(method["note"])}；数据引用：{esc(", ".join(method["evidence_query_ids"]))}</p>')
    content.extend(f'<p>{esc(limit)}</p>' for limit in body["limitations"])
    content.append('<h2>数据来源与审计</h2>')
    content.extend(f'<p>{esc(q["id"])} · query hash: {esc(q["query_hash"])} · 记录数：{q["row_count"]}</p>' for q in evidence["queries"])
    content.append('</section></main>')
    shell_path = settings["layout"].get("shell")
    shell = _inside(Path(resolved["project_root"]), shell_path).read_text(encoding="utf-8") if shell_path else '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dashboard</title></head><body><!-- DASHBOARD_CONTENT --></body></html>'
    shell = shell.replace('<!-- DASHBOARD_CONTENT -->', ''.join(content))
    columns, accent = settings["layout"]["columns"], settings["layout"]["accent"]
    css = f'''<style>
    *{{box-sizing:border-box}}body{{margin:0;background:#f5f7fa;color:#172b4d;font:15px system-ui;line-height:1.6}}
    main.dashboard-container{{max-width:1440px;width:100%;padding:24px;margin:auto}}
    .dashboard-header{{padding:20px 0;border-bottom:2px solid {accent}}}
    .dashboard-header h1,.dashboard-container h2{{color:{accent};overflow-wrap:anywhere}}
    .dashboard-toolbar{{display:flex;flex-wrap:wrap;gap:16px;align-items:center;margin:18px 0}}
    .dashboard-container button{{padding:8px 14px;border:1px solid #ccd5e0;border-radius:6px;cursor:pointer;background:white;color:#172b4d}}
    .kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin:20px 0}}
    .kpi-card{{min-width:0;overflow-wrap:anywhere;padding:20px;background:white;border:1px solid #dce3eb;border-radius:12px}}
    .kpi-card strong{{font-size:30px}}.kpi-card p{{font-size:13px}}
    .dashboard-grid{{display:grid;grid-template-columns:repeat({columns},minmax(0,1fr));gap:18px;align-items:start}}
    .chart-card-header{{min-width:0;overflow-wrap:anywhere}}
    .dashboard-wide,.chart-card--wide{{grid-column:1/-1}}
    .dashboard-container section,.table-scroll{{min-width:0}}.dashboard-container p{{overflow-wrap:anywhere}}
    .insight-card,.diagnostic-panel{{padding:16px 0}}.table-scroll{{overflow:auto;max-height:360px;background:white}}
    .toast-container{{position:fixed;bottom:20px;right:20px;z-index:1000;background:white;max-width:90vw}}
    @media(max-width:760px){{main.dashboard-container{{padding:12px}}.dashboard-grid,.kpi-grid{{grid-template-columns:minmax(0,1fr)}}}}
    @media print{{.dashboard-toolbar,button,.toast-container{{display:none}}.chart-card{{break-inside:avoid}}}}
    </style>'''
    # Defaults precede user CSS; browser verification enforces resolved layout.
    shell = re.sub(r'<head\b[^>]*>', lambda m: m[0] + css, shell, count=1, flags=re.I)
    contract = {"version": 1, "snapshot": {k: resolved[k] for k in ("kind", "profile", "settings", "assets")},
                "profile_sha256": resolved["sha256"], "methods": body["methods"], "chart_choices": choices,
                "kpis": kpis, "placements": [{"id": c["id"], "section": c["section"], "full_width": c["full_width"]} for c in charts]}
    payload = f'<script id="{CONTRACT_ID}" type="application/json">{json_script(contract)}</script>'
    if evidence.get("comparisons"):
        payload += f'<script id="analysis-comparison-contract" type="application/json">{json_script({"version": 1, "comparisons": evidence["comparisons"]})}</script>'
    return re.sub(r'</body\s*>', lambda _: payload + '</body>', shell, flags=re.I)


def add_runtime(content):
    """Keep compiler-owned SVG instances; no pretend refresh or implicit polling."""
    runtime = '''
class ProjectDashboardController extends DashboardController {
  init() { this.theme = 'light'; this.setupEventListeners(); }
  getChart(id) { return echarts.getInstanceByDom(document.getElementById(id)); }
}
window.dashboard = new ProjectDashboardController({charts: window.dashboardCharts, config: {title: document.title}});
for (const root of document.querySelectorAll('[data-echart-chart]')) {
  const button = document.createElement('button');
  button.type = 'button'; button.textContent = '下载 SVG'; button.dataset.downloadChart = root.id;
  button.addEventListener('click', () => window.dashboard.downloadChart(root.id, root.id + '.svg'));
  root.parentElement.appendChild(button);
}
'''
    payload = ''.join('<script>' + (ROOT / "assets/dashboard" / name).read_text(encoding="utf-8") + '</script>'
                      for name in ("html2canvas.min.js", "jspdf.umd.min.js", "dashboard.js"))
    # Vendor JS can contain literal </body> strings. Only touch the actual final
    # closing tag, never regex-replace HTML-like text inside the inlined library.
    end = content.lower().rfind('</body>')
    if end < 0:
        raise ValueError("Dashboard HTML is missing its closing body tag")
    return content[:end] + payload + '<script>' + runtime + '</script>' + content[end:]


def validate_dashboard_contract(path, content, contract, evidence, configs):
    fields = {"id", "label", "unit", "scope", "query_id", "row", "field"}
    expected = load_kpis([{k: v for k, v in spec.items() if k in fields} for spec in contract["kpis"]], evidence, Path(path).parent)
    if expected != contract["kpis"]:
        raise ValueError("Dashboard KPI values differ from query evidence")
    class Inspector(HTMLParser):
        def __init__(self):
            super().__init__()
            self.values, self.active, self.cards = {}, None, []
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if "data-kpi-value" in attrs:
                key = attrs["data-kpi-value"]
                if key in self.values:
                    raise ValueError("Duplicate rendered KPI")
                self.values[key], self.active = "", key
            if "chart-card" in attrs.get("class", "").split():
                self.cards.append("chart-card--wide" in attrs["class"].split())
        def handle_data(self, data):
            if self.active is not None:
                self.values[self.active] += data
        def handle_endtag(self, tag):
            if tag == "strong":
                self.active = None
    inspector = Inspector()
    inspector.feed(content)
    if inspector.values != {k["id"]: str(k["value"]) for k in expected}:
        raise ValueError("Rendered KPI does not match evidence")
    placements = contract["placements"]
    if placements != [{"id": c["id"], "section": c["input"]["section"], "full_width": c["input"]["full_width"]} for c in configs]:
        raise ValueError("Dashboard compiled layout differs from profile contract")
    ordered = [p for section in contract["snapshot"]["settings"]["layout"]["sections"] for p in placements if p["section"] == section["id"]]
    if inspector.cards != [p["full_width"] for p in ordered]:
        raise ValueError("Dashboard card spans differ from compiled layout")


if __name__ == "__main__":
    raise SystemExit(shared.main(kind="dashboard"))
