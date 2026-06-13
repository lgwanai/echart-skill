#!/usr/bin/env python3
"""
Template Builder — Build self-contained HTML from a template + data JSON.

Usage:
    python scripts/build_template.py <template_path> <data_json_path> [--output output.html]

    # Or import:
    from scripts.build_template import build
    build("references/templates/bar/basic.html", {"TITLE": "...", "CATEGORIES": [...], "VALUES": [...]})

Architecture:
    1. Read template HTML
    2. Replace <!-- {{ECHARTS_INLINE}} --> with inline echarts.min.js
    3. Replace {{VAR}} placeholders with JSON data
    4. Write self-contained HTML output

The output is a single .html file that works offline in any browser —
no external URLs, no CDN, no file references.
"""

import json
import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ECHARTS_JS = BASE_DIR / "assets" / "echarts" / "echarts.min.js"


def _load_echarts_js():
    """Load and return the minified ECharts library as a string."""
    if not ECHARTS_JS.exists():
        raise FileNotFoundError(f"ECharts library not found: {ECHARTS_JS}")
    with open(ECHARTS_JS, "r", encoding="utf-8") as f:
        return f.read()


def _json_safe(value):
    """Convert a Python value to valid JS syntax for template insertion.

    All values are produced as valid JS expressions:
    - Lists/dicts → JSON literal: [1,2,3] or {"name":"A"}
    - Strings → JS-quoted: 'horizontal' or '60%'
    - Numbers → number literal: 123
    - bool/None → true/false/null
    - JSON-prefixed strings (starts with [ or {) → raw JSON (for inline JS expressions)
    """
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, str):
        stripped = value.strip()
        # JS keywords — return bare
        if stripped in ("true", "false", "null", "undefined"):
            return stripped
        # JS function / arrow function — return raw
        if stripped.startswith("function") or stripped.startswith("("):
            return stripped
        # Already valid JSON array/object → raw JS expression
        if (stripped.startswith("[") and stripped.endswith("]")) or \
           (stripped.startswith("{") and stripped.endswith("}")):
            try:
                json.loads(stripped)
                return stripped
            except json.JSONDecodeError:
                pass
        # Numeric string like "123" or "3.14" → raw number
        try:
            float(stripped)
            return stripped
        except ValueError:
            pass
        return _js_string(value)
    return str(value)


def _js_string(s):
    """Wrap a string as a valid JS single-quoted string literal."""
    escaped = s.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def build(template_path, data=None, output_path=None):
    """
    Build a self-contained HTML file from a template.

    Args:
        template_path: Path to the .html template file
        data: Dict of placeholder values (e.g. {"TITLE": "图表", "CATEGORIES": [...]})
              If a value is a string starting with '{' or '[', it's treated as raw JSON
              and inserted without extra quoting.
        output_path: Output path. If None, prints to stdout.

    Returns:
        The final HTML string.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    MAPS_DIR = BASE_DIR / "assets" / "echarts"

    # Step 1: Replace fixed markers (don't depend on data)
    echarts_js = _load_echarts_js()
    html = html.replace("<!-- {{ECHARTS_INLINE}} -->", f'<script>\n{echarts_js}\n</script>')

    gl_path = MAPS_DIR / "echarts-gl.min.js"
    if "<!-- {{GL_INLINE}} -->" in html:
        if gl_path.exists():
            with open(gl_path, "r", encoding="utf-8") as f:
                html = html.replace("<!-- {{GL_INLINE}} -->", f'<script>\n{f.read()}\n</script>')
        else:
            html = html.replace("<!-- {{GL_INLINE}} -->",
                                "<!-- echarts-gl.min.js not found — 3D charts will not render -->")

    # Step 2: Save MAP_INLINE flag BEFORE data replacement
    has_map_inline = "{{MAP_INLINE}}" in html or "{{MAP_INLINE}}" in data.get("MAP_INLINE","")

    # Replace all {{PLACEHOLDER}} variables
    if data:
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"  # {{KEY}}
            html = html.replace(placeholder, _json_safe(value))

    # Step 3: Map injection
    if has_map_inline:
        # Find all map names in the processed HTML (supports 'map', 'geo', 'series-map')
        # Patterns: map: 'china'  map: "guangdong"  geo: { map: 'beijing' }
        map_names = set(re.findall(r"""map['\"]\s*:\s*['\"]([\w-]+)['\"]""", html))
        # Also check bmap mode
        if re.search(r'coordinateSystem:\s*[\'"]bmap[\'"]', html):
            map_names.add("bmap")

        injected = []
        for map_name in map_names:
            map_path = MAPS_DIR / f"{map_name}.js"
            if map_path.exists():
                with open(map_path, "r", encoding="utf-8") as f:
                    injected.append(f'<script>\n{f.read()}\n</script>')
            else:
                injected.append(f"<!-- map '{map_name}.js' not found — region may not render -->")

        if injected:
            html = html.replace("<!-- {{MAP_INLINE}} -->", "\n".join(injected))
        else:
            html = html.replace("<!-- {{MAP_INLINE}} -->",
                                "<!-- no map detected → inject default china.js -->\n" +
                                f'<script>\n{MAPS_DIR.joinpath("china.js").read_text()}\n</script>')

    # Post-process: TITLE in HTML context — strip JS quotes added by _json_safe
    # _json_safe wraps strings as 'value', but HTML text needs bare text
    html = re.sub(
        r"<title>'([^']*)'</title>",
        r'<title>\1</title>',
        html
    )
    html = re.sub(
        r'(<div[^>]*id="title"[^>]*>)\'([^\']*)\'(</div>)',
        r'\1\2\3',
        html
    )

    # Step 3: Write output
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Built: {output_path} ({len(html)} bytes)", file=sys.stderr)
    else:
        print(html)

    return html


# ── CLI ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build self-contained HTML from a template")
    parser.add_argument("template", help="Path to template .html file")
    parser.add_argument("--data", "-d", help="Path to data JSON file with { key: value } pairs")
    parser.add_argument("--output", "-o", help="Output HTML file path")
    args = parser.parse_args()

    data = {}
    if args.data:
        with open(args.data, "r", encoding="utf-8") as f:
            data = json.load(f)

    build(args.template, data, args.output)
