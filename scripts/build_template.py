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
    """Convert a Python value to a template-safe string.

    Rules:
    - Lists & dicts → JSON string (e.g. [1,2,3] or {"name":"A"})
    - bool → "true" / "false"
    - None → "null"
    - number → string representation
    - string that looks like JSON (starts with { or [) → use as-is (JS code injection)
    - plain string → use as-is (for HTML text like title, no extra quotes)
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
        # If it's already valid JSON array/object, insert raw (for inline JS)
        if (stripped.startswith("[") and stripped.endswith("]")) or \
           (stripped.startswith("{") and stripped.endswith("}")):
            try:
                json.loads(stripped)
                return stripped
            except json.JSONDecodeError:
                pass
        # Plain string (TITLE, label text, etc.) — no extra JSON quotes
        return value
    return str(value)


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

    # Step 1a: Replace ECharts inline marker
    echarts_js = _load_echarts_js()
    html = html.replace("<!-- {{ECHARTS_INLINE}} -->", f'<script>\n{echarts_js}\n</script>')

    # Step 1b: Replace ECharts GL inline marker (3D charts)
    gl_path = BASE_DIR / "assets" / "echarts" / "echarts-gl.min.js"
    if "<!-- {{GL_INLINE}} -->" in html:
        if gl_path.exists():
            with open(gl_path, "r", encoding="utf-8") as f:
                gl_js = f.read()
            html = html.replace("<!-- {{GL_INLINE}} -->", f'<script>\n{gl_js}\n</script>')
        else:
            html = html.replace("<!-- {{GL_INLINE}} -->",
                                "<!-- echarts-gl.min.js not found — 3D charts will not render -->")

    # Step 1c: Replace Map inline marker — auto-detect map name from template content
    if "<!-- {{MAP_INLINE}} -->" in html:
        # Detect which map is needed: look for map: 'NAME' or map: "NAME" in the template
        map_match = re.search(r"map:\s*['\"](\w+)['\"]", html)
        map_name = map_match.group(1) if map_match else "china"
        map_path = BASE_DIR / "assets" / "echarts" / f"{map_name}.js"
        if map_path.exists():
            with open(map_path, "r", encoding="utf-8") as f:
                map_js = f.read()
            html = html.replace("<!-- {{MAP_INLINE}} -->", f'<script>\n{map_js}\n</script>')
        else:
            html = html.replace("<!-- {{MAP_INLINE}} -->",
                                f"<!-- map '{map_name}.js' not found in assets/echarts/ -->")

    # Step 2: Replace all {{PLACEHOLDER}} variables
    if data:
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"  # {{KEY}}
            html = html.replace(placeholder, _json_safe(value))

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
