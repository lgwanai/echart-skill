#!/usr/bin/env python3
"""Compile explicit data mappings into offline chart components; never infer metrics."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SUPPORTED = {
    "bar",
    "column",
    "line",
    "area",
    "stacked_bar",
    "stacked_area",
    "scatter",
    "pie",
    "mixed",
}


def json_script(value):
    return (
        json.dumps(value, ensure_ascii=False, allow_nan=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def compile_chart(spec, rows):
    """Return deterministic options, using exactly one row per category (no hidden aggregation)."""
    view = spec.get("view")
    if view not in SUPPORTED:
        raise ValueError(
            f"Unsupported compiled view: {view}; use an explicitly verified custom recipe"
        )
    for field in ("id", "title", "scope", "source", "query_hash", "x"):
        if not isinstance(spec.get(field), str) or not spec[field].strip():
            raise ValueError(f"{field} must be a nonempty string")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", spec["id"]):
        raise ValueError("id must be a safe, unique HTML identifier")
    metrics = spec.get("metrics")
    if not isinstance(metrics, list) or not metrics or len(metrics) > 8:
        raise ValueError("metrics requires 1–8 explicit field/name/unit mappings")
    if (
        not isinstance(rows, list)
        or not rows
        or not all(isinstance(row, dict) for row in rows)
    ):
        raise ValueError(
            "rows must be a nonempty array of objects; empty data needs an explicit no-data presentation"
        )
    if len(rows) > 10000:
        raise ValueError("More than 10000 rows: aggregate explicitly before rendering")
    for metric in metrics:
        if not isinstance(metric, dict) or any(
            not isinstance(metric.get(k), str) or not metric[k]
            for k in ("field", "name", "unit")
        ):
            raise ValueError("Each metric needs field, name and unit")
    if len({m["field"] for m in metrics}) != len(metrics) or len(
        {m["name"] for m in metrics}
    ) != len(metrics):
        raise ValueError("Duplicate metric fields/names")
    x = spec["x"]
    if any(
        x not in row or row[x] is None or isinstance(row[x], (dict, list, bool))
        for row in rows
    ):
        raise ValueError("Missing/invalid category or x value")
    categories = [str(row[x]) for row in rows]
    if view != "scatter" and len(set(categories)) != len(categories):
        raise ValueError(
            "Duplicate categories: aggregate or pivot explicitly; never silently overwrite rows"
        )
    if (
        view in {"line", "area", "stacked_area", "mixed"}
        and spec.get("x_order") != "explicit"
    ):
        raise ValueError(
            "Time/ordered charts require x_order=explicit and SQL ORDER BY for the intended calendar"
        )
    values = []
    for metric in metrics:
        column = []
        for row in rows:
            if metric["field"] not in row:
                raise ValueError(f"Missing metric field {metric['field']}")
            value = row[metric["field"]]
            if value is not None and (
                type(value) not in (int, float)
                or abs(value) > 2**53 - 1
                or not math.isfinite(value)
            ):
                raise ValueError(
                    "Metrics must be finite, JS-safe JSON numbers or null; numeric strings, bool, NaN/Infinity and unsafe magnitudes are rejected"
                )
            column.append(value)
        if all(value is None for value in column):
            raise ValueError("All-null metric has no renderable evidence")
        values.append(column)
    units = list(dict.fromkeys(m["unit"] for m in metrics))
    if view != "mixed" and len(units) > 1:
        raise ValueError("Different units require separate charts or mixed dual axes")
    if view == "mixed" and (
        len(metrics) != 2 or [m.get("type") for m in metrics] != ["bar", "line"]
    ):
        raise ValueError(
            "mixed requires exactly bar then line; each receives its own axis"
        )
    option = {
        "animation": False,
        "aria": {"enabled": True, "decal": {"show": True}},
        "tooltip": {
            "trigger": "item" if view in {"pie", "scatter"} else "axis",
            "renderMode": "richText",
        },
        "legend": {"type": "scroll", "top": 0},
        "series": [],
    }
    if view == "pie":
        if (
            len(metrics) != 1
            or not 2 <= len(rows) <= 3
            or any(v is None or v <= 0 for v in values[0])
        ):
            raise ValueError(
                "Pie requires 2–3 strictly positive categories and one metric"
            )
        option["series"] = [
            {
                "name": metrics[0]["name"],
                "type": "pie",
                "radius": [0, "65%"],
                "data": [
                    {"name": c, "value": v} for c, v in zip(categories, values[0])
                ],
            }
        ]
    elif view == "scatter":
        if len(metrics) != 1 or not spec.get("x_unit"):
            raise ValueError("Scatter requires one y metric and x_unit")
        if (
            any(
                type(row[x]) not in (float, int)
                or abs(row[x]) > 2**53 - 1
                or not math.isfinite(row[x])
                for row in rows
            )
            or None in values[0]
        ):
            raise ValueError("Scatter requires finite x/y pairs")
        option.update(
            xAxis={"type": "value", "name": spec["x_unit"], "scale": True},
            yAxis={"type": "value", "name": units[0], "scale": True},
            grid={
                "left": 65,
                "right": 65,
                "top": 65,
                "bottom": 55,
                "containLabel": True,
            },
        )
        option["series"] = [
            {
                "name": metrics[0]["name"],
                "type": "scatter",
                "data": [[r[x], v] for r, v in zip(rows, values[0])],
            }
        ]
    else:
        horizontal = view in {"bar", "stacked_bar"}
        if len(rows) > (40 if horizontal else 1500):
            raise ValueError(
                "Too many categories for a readable chart; aggregate or choose another view"
            )
        category_axis = {
            "type": "category",
            "data": categories,
            "axisLabel": {"hideOverlap": True},
            "inverse": horizontal,
        }
        value_axis = {"type": "value", "name": units[0]}
        option.update(
            xAxis=value_axis if horizontal else category_axis,
            yAxis=category_axis if horizontal else value_axis,
            grid={
                "left": 65,
                "right": 75,
                "top": 65,
                "bottom": 65,
                "containLabel": True,
            },
        )
        if view == "mixed":
            option["yAxis"] = [
                {"type": "value", "name": f"{m['name']} ({m['unit']})"} for m in metrics
            ]
        for index, (metric, data) in enumerate(zip(metrics, values)):
            series = {
                "name": metric["name"],
                "type": (
                    metric["type"]
                    if view == "mixed"
                    else ("line" if view in {"line", "area", "stacked_area"} else "bar")
                ),
                "data": data,
            }
            if series["type"] == "line":
                series.update(connectNulls=False, smooth=False)
            if view in {"area", "stacked_area"}:
                series["areaStyle"] = {}
            if view.startswith("stacked_"):
                series["stack"] = "total"
            if view == "mixed":
                series["yAxisIndex"] = index
            option["series"].append(series)
    return option


def build_html(
    document, base: Path, shell: str | None = None, output_dir: Path | None = None
):
    charts = document.get("charts", [])
    if not isinstance(charts, list) or not charts:
        raise ValueError("charts must be nonempty")
    configs, cards, ids = [], [], set()
    for spec in charts:
        if "rows" in spec:
            raise ValueError(
                "Use rows_path to reference query results, not manually copied rows"
            )
        path = (base / spec["rows_path"]).resolve()
        rows = json.loads(path.read_text(encoding="utf-8"))
        option = compile_chart(spec, rows)
        if spec["id"] in ids:
            raise ValueError("Duplicate chart id")
        ids.add(spec["id"])
        configs.append(
            {
                "id": spec["id"],
                "option": option,
                "input": spec,
                "result_ref": (
                    os.path.relpath(path, output_dir.resolve())
                    if output_dir
                    else str(path)
                ),
                "result_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
        columns = [spec["x"], *[m["field"] for m in spec["metrics"]]]
        esc = lambda value: html.escape(str(value), quote=True)
        header = "".join(f"<th>{esc(c)}</th>" for c in columns)
        body = "".join(
            "<tr>"
            + "".join(
                f'<td>{esc(row[c]) if row[c] is not None else "—"}</td>'
                for c in columns
            )
            + "</tr>"
            for row in rows
        )
        height = (
            max(360, len(rows) * 26 + 130)
            if spec["view"] in {"bar", "stacked_bar"}
            else 400
        )
        cards.append(
            f'<section class="chart-card"><h2>{esc(spec["title"])}</h2>'
            f'<p>统计口径：{esc(spec["scope"])} · 数据来源：{esc(spec["source"])} · query hash: {esc(spec["query_hash"])}</p>'
            f'<div id="{spec["id"]}" class="chart-surface" data-echart-chart aria-label="{esc(spec["title"])}" style="height:{height}px"></div>'
            f'<details class="chart-data-table" data-chart-table="{spec["id"]}"><summary>查看数据</summary><div class="table-scroll"><table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table></div></details></section>'
        )
    if shell is None:
        shell = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>数据图表</title></head><body><main><!-- ECHART_CHARTS --></main></body></html>'
    if (
        shell.count("<!-- ECHART_CHARTS -->") != 1
        or shell.lower().count("</body>") != 1
        or shell.lower().count("</head>") != 1
    ):
        raise ValueError("Shell needs one ECHART_CHARTS marker, </head>, and </body>")
    if re.search(r"echarts(?:\.min)?\.js|echarts\.init", shell):
        raise ValueError("Shell must not include a second ECharts library/bootstrap")
    css = "<style>main{max-width:1280px;margin:auto;padding:16px;font:15px system-ui}.chart-card{min-width:0;padding:16px;margin-bottom:18px;border:1px solid #dce3eb;border-radius:12px;background:white}.chart-surface{width:100%;min-width:0}.table-scroll{overflow:auto;max-height:360px}th,td{padding:8px;border-bottom:1px solid #ddd;text-align:left}summary{cursor:pointer}p{overflow-wrap:anywhere}body{margin:0;background:#f5f7fa;color:#172b4d}</style>"
    shell = re.sub("</head>", lambda _: css + "</head>", shell, count=1, flags=re.I)
    shell = shell.replace(
        "<!-- ECHART_CHARTS -->",
        "".join(cards)
        + "<p>生成时间："
        + datetime.now(timezone.utc).isoformat(timespec="seconds")
        + "</p>",
    )
    library = (ROOT / "assets/echarts/echarts.min.js").read_text(encoding="utf-8")
    runtime = (ROOT / "assets/chart_runtime.js").read_text(encoding="utf-8")
    payload = f'<script id="chart-build-spec" type="application/json">{json_script(configs)}</script><script>{library}</script><script>{runtime}</script>'
    return re.sub("</body>", lambda _: payload + "</body>", shell, count=1, flags=re.I)


def validate_compiled_html(path):
    from html.parser import HTMLParser
    from scripts.artifact_manifest import _extract_json_script, MANIFEST_ID

    class Extract(HTMLParser):
        def __init__(self):
            super().__init__()
            self.active = False
            self.chunks = []

        def handle_starttag(self, tag, attrs):
            if tag == "script":
                self.active = dict(attrs).get("id") == "chart-build-spec"

        def handle_endtag(self, tag):
            if tag == "script":
                self.active = False

        def handle_data(self, data):
            if self.active:
                self.chunks.append(data)

    parser = Extract()
    content = Path(path).read_text(encoding="utf-8")
    parser.feed(content)
    if not parser.chunks:
        return []
    errors = []
    try:
        configs = json.loads("".join(parser.chunks))
        if not isinstance(configs, list) or not configs:
            raise ValueError("Compiled chart list must be nonempty")
        manifest, _ = _extract_json_script(content, MANIFEST_ID)
        for config in configs:
            source = Path(config["result_ref"])
            if not source.is_absolute():
                source = Path(path).parent / source
            raw = source.read_bytes()
            if hashlib.sha256(raw).hexdigest() != config["result_sha256"]:
                errors.append(f"{config['id']}: query result changed since compilation")
            expected = compile_chart(config["input"], json.loads(raw))
            if expected != config["option"]:
                errors.append(
                    f"{config['id']}: compiled option differs from query results/mapping"
                )
            if manifest is not None:
                matches = [
                    q
                    for q in manifest.get("queries", [])
                    if q.get("query_hash") == config["input"]["query_hash"]
                    and q.get("result_sha256") == config["result_sha256"]
                    and (Path(path).parent / q.get("result_ref", "")).resolve()
                    == source.resolve()
                ]
                if not matches:
                    errors.append(
                        f"{config['id']}: chart source/query hash is not bound in evidence manifest"
                    )
    except (ValueError, KeyError, OSError, TypeError) as exc:
        errors.append(f"Invalid compiled chart contract: {exc}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--shell",
        type=Path,
        help="Agent-authored report/dashboard shell with ECHART_CHARTS marker",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        help="Bind this evidence draft and require the full delivery gate before publishing output",
    )
    args = parser.parse_args()
    try:
        document = json.loads(args.spec.read_text(encoding="utf-8"))
        content = build_html(
            document,
            args.spec.resolve().parent,
            args.shell.read_text(encoding="utf-8") if args.shell else None,
            args.output.parent,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.evidence:
            from scripts.artifact_manifest import materialize_manifest, embed_manifest
            from scripts.validate_delivery import validate_delivery

            draft = json.loads(args.evidence.read_text(encoding="utf-8"))
            with tempfile.NamedTemporaryFile(
                dir=args.output.parent,
                prefix=args.output.stem + "-",
                suffix=".html",
                delete=False,
            ) as handle:
                candidate = Path(handle.name)
            try:
                candidate.write_text(content, encoding="utf-8")
                embed_manifest(
                    candidate, materialize_manifest(draft, args.evidence, candidate)
                )
                errors = validate_delivery(candidate)
                if errors:
                    raise ValueError("; ".join(errors))
                candidate.replace(args.output)
            finally:
                candidate.unlink(missing_ok=True)
        else:
            args.output.write_text(content, encoding="utf-8")
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(1, f"Build rejected: {exc}\n")
    print(
        f"Verified output: {args.output}"
        if args.evidence
        else f"Built draft: {args.output}. Bind evidence, then run validate_delivery.py before delivery."
    )


if __name__ == "__main__":
    main()
