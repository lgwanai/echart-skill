"""
Hard-check: validate generated chart HTML has renderable ECharts config.
Run after Agent generates a chart. Auto-detects and reports issues.
Usage: python scripts/validate_chart.py <path/to/chart.html>
Exit code 0 = valid, 1 = invalid (with error details)
"""
import re, sys, os, json, subprocess, tempfile, shutil
from html.parser import HTMLParser


class _HTMLAssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.scripts = []
        self._script_attrs = None
        self._script_chunks = []

    def handle_starttag(self, tag, attrs):
        attr_map = {name.lower(): value for name, value in attrs}
        tag = tag.lower()
        self.tags.append((tag, attr_map))
        if tag == "script":
            self._script_attrs = attr_map
            self._script_chunks = []

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self._script_attrs is not None:
            self.scripts.append((self._script_attrs, "".join(self._script_chunks)))
            self._script_attrs = None
            self._script_chunks = []

    def handle_data(self, data):
        if self._script_attrs is not None:
            self._script_chunks.append(data)


def _parse_html(content):
    parser = _HTMLAssetParser()
    parser.feed(content)
    return parser


def _strip_js_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//[^\n\r]*", "", text)


def _extract_balanced(text, start_index, opener, closer):
    depth = 0
    in_string = None
    escape = False
    for index in range(start_index, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == in_string:
                in_string = None
            continue
        if char in ("'", '"', "`"):
            in_string = char
        elif char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return text[start_index:index + 1]
    return ""


def _check_script_tag_integrity(content):
    """Detect the #1 blank-page bug: a <script> block that never properly closes.

    Browsers only terminate a <script> on a *literal* ``</script>``. If the
    inlined ECharts library (or any inline block) is closed with an escaped
    ``<\\/script>`` — the JS-string escape wrongly applied to the real HTML
    closing tag — the browser ignores it and swallows the entire rest of the
    document (page body + every chart bootstrap) as script text. The page
    renders completely blank, yet Python's HTMLParser silently scans past the
    escaped tag to the next real ``</script>``, so the structural checks below
    still see a "valid" inlined library. This raw-text check is the only place
    that catches it.
    """
    errors = []

    if _has_escaped_script_close_outside_js_string(content):
        errors.append(
            "BLANK PAGE: found escaped `<\\/script>` closing tag — the browser "
            "does NOT recognize it, so the <script> block never closes and the "
            "whole page renders blank. Write the inline library's closing tag as "
            "a literal `</script>` (backslash-escaping only belongs inside JS "
            "string literals, never on the real tag)."
        )

    # Opening/closing <script> tag balance for real HTML tags. Do not count
    # escaped/script-like strings inside inlined libraries such as jsPDF.
    parsed = _parse_html(content)
    open_tags = sum(1 for tag, _attrs in parsed.tags if tag == "script")
    close_tags = len(parsed.scripts)
    if open_tags != close_tags:
        errors.append(
            f"BLANK PAGE: unbalanced <script> tags ({open_tags} open vs "
            f"{close_tags} close) — an inline block is not properly terminated "
            f"and will consume the rest of the document as script text. Every "
            f"`<script>` (including the inlined ECharts library) needs a matching "
            f"literal `</script>`."
        )

    return errors


def _has_escaped_script_close_outside_js_string(content):
    script_open = re.compile(r"<script\b[^>]*>", re.IGNORECASE)
    literal_close = re.compile(r"</script\s*>", re.IGNORECASE)
    escaped_close = re.compile(r"<\\/script\s*>", re.IGNORECASE)

    pos = 0
    while True:
        open_match = script_open.search(content, pos)
        if not open_match:
            return False
        close_match = literal_close.search(content, open_match.end())
        script_end = close_match.start() if close_match else len(content)
        script_body = content[open_match.end():script_end]
        if _escaped_script_close_outside_string(script_body, escaped_close):
            return True
        if not close_match:
            return False
        pos = close_match.end()


def _escaped_script_close_outside_string(script_body, escaped_close_pattern):
    in_string = None
    escape = False
    index = 0
    while index < len(script_body):
        if escaped_close_pattern.match(script_body, index) and in_string is None:
            return True
        char = script_body[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif in_string == "`" and char == "$" and index + 1 < len(script_body) and script_body[index + 1] == "{":
                # Template expression parsing is intentionally conservative;
                # keep treating it as string for this check because generated
                # dashboard data should never need raw closing script tags.
                pass
            elif char == in_string:
                in_string = None
        elif char in ("'", '"', "`"):
            in_string = char
        index += 1
    return False


def _extract_report_chart_specs(content):
    marker = "window.reportChartSpecs"
    marker_index = content.find(marker)
    if marker_index < 0:
        return []
    assignment_index = content.find("=", marker_index)
    if assignment_index < 0:
        return []
    array_start = content.find("[", assignment_index)
    if array_start < 0:
        return []
    raw_array = _extract_balanced(content, array_start, "[", "]")
    if not raw_array:
        return []
    try:
        specs = json.loads(raw_array)
    except json.JSONDecodeError:
        return []
    return specs if isinstance(specs, list) else []


def _is_probably_vendor_script(script):
    vendor_markers = [
        "Apache ECharts",
        "echarts.registerMap",
        "html2canvas",
        "jsPDF",
        "jspdf.umd",
        "sourceMappingURL=jspdf",
        "DOMPurify",
    ]
    if any(marker in script for marker in vendor_markers) and len(script) > 50000:
        return True
    return len(script) > 300000


def _is_echarts_library_script(script):
    return (
        len(script) > 100000
        and "echarts" in script
        and (
            "Apache Software Foundation" in script
            or ".echarts={}" in script
            or "echarts={}" in script
            or "version:\"6." in script
            or "version:'6." in script
            or "version:\"5." in script
            or "version:'5." in script
        )
    )


def _chart_bootstrap_before_echarts(parsed_html):
    first_echarts_library_index = None
    for index, (_, script) in enumerate(parsed_html.scripts):
        if _is_echarts_library_script(script):
            first_echarts_library_index = index
            break
    if first_echarts_library_index is None:
        return False

    for index, (_, script) in enumerate(parsed_html.scripts[:first_echarts_library_index]):
        if (
            "window.dashboardCharts" in script
            or "echarts.init" in script
            or re.search(r"\.setOption\s*\(", script)
        ):
            return True
    return False


def _has_inlined_echarts_library(parsed_html):
    return any(_is_echarts_library_script(script) for _, script in parsed_html.scripts)


def _custom_inline_scripts(parsed_html):
    scripts = []
    for attrs, script in parsed_html.scripts:
        if attrs.get("src"):
            continue
        if not script.strip():
            continue
        if _is_probably_vendor_script(script):
            continue
        scripts.append(script)
    return scripts


def _strip_js_comments(script: str) -> str:
    """Remove JS single-line and multi-line comments, keeping line counts intact."""
    # Remove /* ... */ blocks
    result = re.sub(r"/\*.*?\*/", " ", script, flags=re.DOTALL)
    # Remove // comments (but not URLs like https://)
    result = re.sub(r"(?<!:)//[^\n]*", "", result)
    return result


def _detect_unbalanced_echarts_graphic_calls(scripts):
    errors = []
    pattern = re.compile(r"new\s+echarts\.graphic\.(LinearGradient|RadialGradient)\s*\(")
    for script_index, script in enumerate(scripts, start=1):
        clean = _strip_js_comments(script)
        for match in pattern.finditer(clean):
            call = match.group(1)
            if not _extract_balanced(clean, match.end() - 1, "(", ")"):
                errors.append(
                    f"INVALID JS in custom script #{script_index}: "
                    f"unclosed echarts.graphic.{call}(...) call — "
                    f"close the constructor before closing the option object"
                )
    return errors


def _run_node_syntax_check(scripts):
    node = shutil.which("node")
    if not node:
        return []

    errors = []
    for index, script in enumerate(scripts, start=1):
        wrapped = script
        if "await " in script and "async function" not in script:
            wrapped = f"(async function(){{\n{script}\n}});"
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tmp:
            tmp.write(wrapped)
            tmp_path = tmp.name
        try:
            result = subprocess.run(
                [node, "--check", tmp_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception as exc:
            errors.append(f"JS syntax check failed for custom script #{index}: {exc}")
        else:
            if result.returncode != 0:
                detail = [line for line in (result.stderr or result.stdout).strip().splitlines() if line.strip()]
                useful = [
                    line for line in detail
                    if not line.startswith("Node.js ")
                    and not line.startswith("    at ")
                ]
                syntax_index = next(
                    (i for i, line in enumerate(useful) if "SyntaxError" in line or "Unexpected" in line),
                    None,
                )
                if syntax_index is not None:
                    start = max(0, syntax_index - 3)
                    end = min(len(useful), syntax_index + 2)
                    message = " | ".join(useful[start:end])
                else:
                    message = " | ".join(useful[-5:]) if useful else "unknown syntax error"
                errors.append(f"INVALID JS in custom script #{index}: {message}")
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    return errors


def _unsafe_url(value):
    if value is None:
        return False
    value = value.strip()
    if not value or value.startswith(("#", "data:", "mailto:", "tel:", "javascript:void")):
        return False
    return bool(re.match(r"^(?:https?:)?//|^https?://|^file://", value, re.IGNORECASE))


def _walk_values(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_values(child)


def _chart_types_from_specs(specs):
    types = []
    for spec in specs:
        option = spec.get("option") if isinstance(spec, dict) else None
        for value in _walk_values(option):
            if isinstance(value, dict) and isinstance(value.get("type"), str):
                types.append(value["type"])
    return types


def _specs_have_data(specs):
    for spec in specs:
        option = spec.get("option") if isinstance(spec, dict) else None
        for value in _walk_values(option):
            if isinstance(value, dict):
                data = value.get("data")
                source = value.get("source")
                if isinstance(data, list) and len(data) > 0:
                    return True
                if source is not None:
                    return True
    return False


def _looks_like_dashboard(content, html_path):
    basename = os.path.basename(html_path).lower()
    lower = content.lower()
    init_count = len(re.findall(r"echarts\.init\s*\(", content))
    title_dashboard = bool(re.search(r"<title>[^<]*(dashboard|仪表盘|看板)", lower))
    return (
        "dashboard" in basename
        or "仪表盘" in content
        or "看板" in content
        or title_dashboard
        or init_count >= 2
        or "dashboard-container" in content
        or "dashboard-grid" in content
        or "DashboardController" in content
    )


def _has_html_class(content, class_name):
    return bool(re.search(
        r"class\s*=\s*['\"][^'\"]*\b" + re.escape(class_name) + r"\b",
        content,
        re.IGNORECASE,
    ))


def _detect_raw_page_layout(content):
    lower = content.lower()
    explicit_raw_page = "simplepagelayout" in lower
    page_layout_marker = bool(re.search(
        r"(?:class\s*=\s*['\"][^'\"]*\bpage\b|\.page\s*\{)",
        content,
        re.IGNORECASE,
    ))
    flex_stack_marker = (
        "display:flex;flex-direction:column" in lower
        or "display: flex; flex-direction: column" in lower
    )
    chart_container_count = len(re.findall(r"class\s*=\s*['\"][^'\"]*chart-container", content, re.IGNORECASE))
    return chart_container_count >= 2 and (explicit_raw_page or (page_layout_marker and flex_stack_marker))


def _detect_large_handwritten_data_objects(scripts):
    errors = []
    assignment_pattern = re.compile(
        r"\b(?:const|let|var)\s+(?:DATA|data|dashboardData|chartData)\s*=\s*\{",
    )
    for script_index, script in enumerate(scripts, start=1):
        for match in assignment_pattern.finditer(script):
            raw_object = _extract_balanced(script, match.end() - 1, "{", "}")
            if not raw_object:
                continue
            # Large nested JS object literals are the common source of silent
            # dashboard blank pages. JSON.parse/json.dumps output always has
            # quoted keys, no single-quoted strings, and can be node-checked.
            unquoted_keys = len(re.findall(r"(?<!['\"])\b[A-Za-z_$][\w$]*\s*:", raw_object))
            single_quotes = raw_object.count("'")
            if len(raw_object) > 1200 and (unquoted_keys > 5 or single_quotes > 10):
                errors.append(
                    f"INVALID DATA embedding in custom script #{script_index}: "
                    f"large hand-written JS object assigned to DATA/chartData — "
                    f"serialize data with Python `json.dumps(..., ensure_ascii=False, default=str)` "
                    f"and embed it as `window.dashboardData = JSON.parse(<json string>)` "
                    f"or a strict JSON literal with quoted keys. Do not hand-write nested JS objects."
                )
    return errors


def _css_number_px(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _detect_narrow_fixed_layout(content):
    errors = []
    # Enterprise dashboards should use most desktop viewport width. A main
    # shell fixed around 600-900px creates the common left-column / blank-right
    # failure shown in browser screenshots.
    narrow_shell_pattern = re.compile(
        r"(?:\.|#)(?:dashboard-container|dashboard-shell|dashboard-main|main-content|content|container|wrapper)"
        r"[^{}]*\{[^{}]*(?:max-)?width\s*:\s*(\d+(?:\.\d+)?)px",
        re.IGNORECASE | re.DOTALL,
    )
    for match in narrow_shell_pattern.finditer(content):
        width = _css_number_px(match.group(1))
        if width is not None and width < 1100:
            errors.append(
                f"DASHBOARD LAYOUT: main dashboard shell is fixed/narrow ({width:g}px) — "
                "desktop dashboards must use a responsive full-width container such as "
                "`width: min(100%, 1440px)` or `max-width: 1440px; margin: 0 auto`, "
                "not a narrow left column that leaves blank space."
            )

    narrow_inline_pattern = re.compile(
        r"class\s*=\s*['\"][^'\"]*(?:dashboard-container|dashboard-shell|dashboard-main)[^'\"]*['\"][^>]*"
        r"style\s*=\s*['\"][^'\"]*(?:max-)?width\s*:\s*(\d+(?:\.\d+)?)px",
        re.IGNORECASE | re.DOTALL,
    )
    for match in narrow_inline_pattern.finditer(content):
        width = _css_number_px(match.group(1))
        if width is not None and width < 1100:
            errors.append(
                f"DASHBOARD LAYOUT: inline dashboard shell width is too narrow ({width:g}px) — "
                "use responsive full-width layout constraints."
            )
    return errors


def _detect_dashboard_grid_density_issues(content):
    errors = []
    lower = content.lower()
    has_grid_class = _has_html_class(content, "dashboard-grid") or ".dashboard-grid" in content
    has_grid_css = bool(re.search(
        r"\.dashboard-grid[^{}]*\{[^{}]*display\s*:\s*grid",
        content,
        re.IGNORECASE | re.DOTALL,
    ))
    has_responsive_columns = bool(re.search(
        r"grid-template-columns\s*:\s*(?:repeat\s*\([^;{}]*(?:minmax|auto-fit|auto-fill)|[^;{}]*(?:minmax|fr))",
        content,
        re.IGNORECASE | re.DOTALL,
    ))
    if has_grid_class and (not has_grid_css or not has_responsive_columns):
        errors.append(
            "DASHBOARD LAYOUT: dashboard-grid is not a real responsive CSS Grid — "
            "use `display: grid` with `grid-template-columns: repeat(auto-fit, minmax(...))` "
            "or explicit `fr` columns so desktop views do not collapse into one narrow column."
        )

    chart_card_count = len(_chart_card_opening_tags(content))
    if chart_card_count >= 3 and not has_responsive_columns:
        errors.append(
            "DASHBOARD LAYOUT: 3+ chart cards without responsive multi-column grid — "
            "desktop dashboards need 2-3 column card placement, not a single vertical strip."
        )

    if (
        ("display:flex;flex-direction:column" in lower or "display: flex; flex-direction: column" in lower)
        and chart_card_count >= 3
        and not has_responsive_columns
    ):
        errors.append(
            "DASHBOARD LAYOUT: chart cards are arranged as a vertical flex column — "
            "replace with CSS Grid and responsive columns to avoid left-column whitespace."
        )
    return errors


def _detect_chart_card_dimension_issues(content):
    errors = []
    # Fixed tiny cards/charts make legends and axes unreadable. Keep this check
    # conservative: only block explicit small px dimensions on dashboard chart
    # cards/containers.
    for selector in ("chart-card", "chart-panel", "chart-container", "echart-card", "viz-card"):
        for block in _css_blocks_for_exact_selector(content, selector):
            match = re.search(r"(?:max-)?width\s*:\s*(\d+(?:\.\d+)?)px", block, re.IGNORECASE)
            width = _css_number_px(match.group(1)) if match else None
            if width is not None and width < 520:
                errors.append(
                    f"DASHBOARD LAYOUT: chart card/container width is too small ({width:g}px) — "
                    "use grid tracks with minmax(360px, 1fr) or wider cards for readable axes and legends."
                )

    for selector in ("chart", "chart-card", "chart-panel", "chart-container", "echart-card", "viz-card"):
        for block in _css_blocks_for_exact_selector(content, selector):
            match = re.search(r"(?:height|min-height)\s*:\s*(\d+(?:\.\d+)?)px", block, re.IGNORECASE)
            height = _css_number_px(match.group(1)) if match else None
            if height is not None and height < 300:
                errors.append(
                    f"DASHBOARD LAYOUT: chart area height is too small ({height:g}px) — "
                    "use stable chart heights of at least 320-420px for enterprise dashboards."
                )
    return errors


def _detect_long_table_without_scroll(content):
    table_blocks = re.findall(r"<table\b.*?</table>", content, flags=re.IGNORECASE | re.DOTALL)
    errors = []
    for table in table_blocks:
        row_count = len(re.findall(r"<tr\b", table, flags=re.IGNORECASE))
        table_index = content.find(table)
        context_start = max(0, table_index - 500)
        context_end = min(len(content), table_index + len(table) + 250)
        table_context = content[context_start:context_end]
        has_local_scroll_container = bool(re.search(
            r"(table-scroll|table-wrapper|data-table-container|overflow-y\s*:\s*(?:auto|scroll)|overflow\s*:\s*(?:auto|scroll)|max-height\s*:)",
            table_context,
            re.IGNORECASE,
        ))
        if row_count > 18 and not has_local_scroll_container:
            errors.append(
                f"DASHBOARD LAYOUT: long table has {row_count} rows without a scroll/max-height wrapper — "
                "large detail tables must live inside `.table-scroll`/`.table-wrapper` with "
                "`max-height` and `overflow:auto`, or be paginated/summarized."
            )
            break
    return errors


def _css_blocks_for_selector(content, selector_name):
    pattern = re.compile(
        r"\." + re.escape(selector_name) + r"(?=[\s\*\.:,\{])[^{}]*\{([^{}]*)\}",
        re.IGNORECASE | re.DOTALL,
    )
    return [match.group(1) for match in pattern.finditer(content)]


def _css_blocks_for_exact_selector(content, selector_name):
    pattern = re.compile(
        r"(?:^|[}\n])\s*(?:\.|#)" + re.escape(selector_name) + r"\s*\{([^{}]*)\}",
        re.IGNORECASE | re.DOTALL,
    )
    return [match.group(1) for match in pattern.finditer(content)]


def _detect_card_text_wrap_issues(content):
    errors = []
    checks = [
        ("kpi-card", "KPI cards"),
        ("chart-card-header", "chart card headers"),
    ]
    for class_name, label in checks:
        if class_name not in content:
            continue
        css_blocks = _css_blocks_for_selector(content, class_name)
        combined = "\n".join(css_blocks).lower()
        if re.search(r"white-space\s*:\s*nowrap", combined):
            errors.append(
                f"DASHBOARD LAYOUT: {label} use `white-space: nowrap` — "
                "KPI/card text must wrap predictably instead of forcing cards to overflow."
            )
        has_min_width_zero = bool(re.search(r"min-width\s*:\s*0\b", combined))
        has_wrap = bool(re.search(r"(overflow-wrap\s*:\s*(?:anywhere|break-word)|word-break\s*:\s*break-word)", combined))
        if not has_min_width_zero or not has_wrap:
            errors.append(
                f"DASHBOARD LAYOUT: {label} lack stable wrapping CSS — "
                "add `min-width: 0` plus `overflow-wrap: anywhere` or `word-break: break-word` "
                "so Chinese titles, long metric names, and large values do not break card layout."
            )
    return errors


def _strip_html_tags(text):
    return re.sub(r"<[^>]+>", " ", text)


def _detect_dense_cards_without_span(content):
    errors = []
    card_pattern = re.compile(
        r"<(?P<tag>section|article|div)\b(?P<attrs>[^>]*class\s*=\s*['\"][^'\"]*['\"][^>]*)>"
        r"(?P<body>.*?)</(?P=tag)>",
        re.IGNORECASE | re.DOTALL,
    )
    dense_keywords = (
        "预测",
        "趋势",
        "年度",
        "月度",
        "置信",
        "区间",
        "GMV",
        "forecast",
        "trend",
        "monthly",
        "year",
    )
    for match in card_pattern.finditer(content):
        attrs = match.group("attrs")
        if not _has_class_token(attrs, "chart-card"):
            continue
        body = match.group("body")
        text = _strip_html_tags(body)
        is_dense = any(keyword.lower() in text.lower() for keyword in dense_keywords)
        if not is_dense:
            continue
        has_span = bool(
            re.search(r"\b(chart-card--wide|card-wide|span-2|grid-span-2|full-width|is-wide)\b", attrs, re.IGNORECASE)
            or re.search(r"grid-column\s*:\s*(?:span\s*2|1\s*/\s*-1)", attrs + body, re.IGNORECASE)
        )
        if not has_span:
            title = " ".join(text.split())[:80]
            errors.append(
                f"DASHBOARD LAYOUT: dense chart card `{title}` has no explicit wide/full span — "
                "forecast, trend, monthly, annual, confidence-interval, or GMV charts need "
                "`chart-card--wide`/`span-2`/`full-width` or `grid-column: span 2` to avoid "
                "half-width cards wrapping into broken rows."
            )
    return errors


def _has_class_token(attrs, class_name):
    match = re.search(r"class\s*=\s*['\"]([^'\"]*)['\"]", attrs, re.IGNORECASE | re.DOTALL)
    if not match:
        return False
    return class_name in re.split(r"\s+", match.group(1).strip())


def _chart_card_opening_tags(content):
    tags = []
    for match in re.finditer(
        r"<(?:section|article|div)\b(?P<attrs>[^>]*class\s*=\s*['\"][^'\"]*['\"][^>]*)>",
        content,
        re.IGNORECASE | re.DOTALL,
    ):
        attrs = match.group("attrs")
        if _has_class_token(attrs, "chart-card"):
            tags.append(attrs)
    return tags


def _chart_card_has_effective_span(attrs):
    return bool(
        re.search(r"\b(chart-card--wide|card-wide|span-2|grid-span-2|full-width|is-wide)\b", attrs, re.IGNORECASE)
        or re.search(r"grid-column\s*:\s*(?:span\s*2|1\s*/\s*-1)", attrs, re.IGNORECASE)
    )


def _detect_orphan_half_width_cards(content):
    errors = []
    if not re.search(
        r"\.dashboard-grid[^{}]*\{[^{}]*grid-template-columns\s*:\s*(?:repeat\s*\(\s*2\s*,|[^;{}]*1fr[^;{}]*1fr)",
        content,
        re.IGNORECASE | re.DOTALL,
    ):
        return errors

    card_attrs = _chart_card_opening_tags(content)
    if len(card_attrs) < 5:
        return errors

    ordinary_count = sum(1 for attrs in card_attrs if not _chart_card_has_effective_span(attrs))
    if ordinary_count >= 5 and ordinary_count % 2 == 1:
        errors.append(
            "DASHBOARD LAYOUT: odd number of ordinary half-width chart cards in a two-column dashboard grid — "
            "this creates orphan rows and large blank space like a broken BI page. Make one analytical card "
            "`chart-card--wide`/`full-width` with an effective `grid-column` rule, or add a paired companion card."
        )
    return errors


def _detect_first_dashboard_card_not_wide(content):
    errors = []
    if not re.search(
        r"\.dashboard-grid[^{}]*\{[^{}]*grid-template-columns\s*:\s*(?:repeat\s*\(\s*(?:2|3)\s*,|[^;{}]*1fr[^;{}]*1fr)",
        content,
        re.IGNORECASE | re.DOTALL,
    ):
        return errors

    card_attrs = _chart_card_opening_tags(content)
    if len(card_attrs) < 4:
        return errors
    if not _chart_card_has_effective_span(card_attrs[0]):
        errors.append(
            "DASHBOARD LAYOUT: first analytical chart card is ordinary half-width in a multi-column grid — "
            "enterprise dashboards must make the first core trend/diagnostic chart wide/full so the first "
            "row does not leave a blank right side or bury the main conclusion."
        )
    return errors


def _detect_span_class_css_issues(content):
    errors = []
    span_classes = (
        "chart-card--wide",
        "card-wide",
        "span-2",
        "grid-span-2",
        "full-width",
        "is-wide",
    )
    for class_name in span_classes:
        if class_name not in content:
            continue
        css_blocks = _css_blocks_for_selector(content, class_name)
        has_class_grid_span = any(
            re.search(r"grid-column\s*:\s*(?:span\s*2|1\s*/\s*-1)", block, re.IGNORECASE)
            for block in css_blocks
        )
        has_inline_grid_span = bool(re.search(
            r"class\s*=\s*['\"][^'\"]*\b" + re.escape(class_name) + r"\b[^'\"]*['\"][^>]*"
            r"style\s*=\s*['\"][^'\"]*grid-column\s*:\s*(?:span\s*2|1\s*/\s*-1)",
            content,
            re.IGNORECASE | re.DOTALL,
        ))
        if not has_class_grid_span and not has_inline_grid_span:
            errors.append(
                f"DASHBOARD LAYOUT: `{class_name}` is used but has no effective `grid-column` rule — "
                "wide/full span class names must map to `grid-column: span 2` or `grid-column: 1 / -1`; "
                "otherwise dense dashboard cards still collapse into ordinary half-width placement."
            )
    return errors


def _detect_misapplied_full_width_grid_issues(content):
    errors = []
    row_grid_blocks = _css_blocks_for_selector(content, "row")
    row_grid_is_two_col = any(
        re.search(r"display\s*:\s*grid", block, re.IGNORECASE)
        and re.search(r"grid-template-columns\s*:\s*(?:1fr\s+1fr|repeat\s*\(\s*2\s*,)", block, re.IGNORECASE)
        for block in row_grid_blocks
    )
    if not row_grid_is_two_col:
        return errors

    row_full_pattern = re.compile(
        r"<(?P<tag>section|article|div|main)\b(?P<attrs>[^>]*class\s*=\s*['\"][^'\"]*\brow\b[^'\"]*\bfull\b[^'\"]*['\"][^>]*)>"
        r"(?P<body>.*?)</(?P=tag)>",
        re.IGNORECASE | re.DOTALL,
    )
    for match in row_full_pattern.finditer(content):
        body = match.group("body")
        card_like_children = len(re.findall(r"class\s*=\s*['\"][^'\"]*\b(?:card|chart-card)\b", body, re.IGNORECASE))
        dense_text = _strip_html_tags(body)
        has_dense_chart = any(
            keyword.lower() in dense_text.lower()
            for keyword in ("趋势", "月度", "年度", "GMV", "预测", "forecast", "trend", "monthly", "year")
        )
        if card_like_children <= 1 or has_dense_chart:
            title = " ".join(dense_text.split())[:80]
            errors.append(
                f"DASHBOARD LAYOUT: pseudo full-width row `{title}` uses `class=\"row full\"` on a "
                "two-column grid container — `grid-column` on the row itself does not make its single "
                "child card span both columns. Use one `.dashboard-grid` parent and put "
                "`chart-card--wide`/`full-width`/`grid-column: 1 / -1` on the actual chart card."
            )
            break
    return errors


def _count_chart_shells(content):
    return len(_chart_card_opening_tags(content)) + len(re.findall(
        r"<(?:section|article|div)\b[^>]*class\s*=\s*['\"][^'\"]*\bchart-panel\b",
        content,
        re.IGNORECASE | re.DOTALL,
    ))


def _detect_missing_chart_governance_and_data_access(content, is_dashboard):
    errors = []
    chart_shell_count = _count_chart_shells(content)
    if chart_shell_count == 0:
        if "echarts.init" in content:
            errors.append(
                "CHART GOVERNANCE: ECharts output has no chart-card/chart-panel shell — "
                "every chart must live in an enterprise chart container with title, scope, source, and data access."
            )
        return errors

    data_button_count = len(re.findall(
        r"(?:data-action\s*=\s*['\"]view-data['\"]|data-role\s*=\s*['\"]view-data['\"]|查看数据)",
        content,
        re.IGNORECASE,
    ))
    data_table_count = len(re.findall(
        r"class\s*=\s*['\"][^'\"]*\b(?:chart-data-table|data-table-panel|chart-data-modal)\b",
        content,
        re.IGNORECASE,
    ))
    hidden_table_count = len(re.findall(
        r"(?:hidden|display\s*:\s*none|aria-hidden\s*=\s*['\"]true['\"]|class\s*=\s*['\"][^'\"]*\bis-hidden\b)",
        content,
        re.IGNORECASE,
    ))

    if data_button_count < chart_shell_count:
        errors.append(
            f"CHART GOVERNANCE: {chart_shell_count} chart cards/panels but only {data_button_count} visible data buttons — "
            "each chart must include a `查看数据` button (`data-action=\"view-data\"` or `data-role=\"view-data\"`)."
        )
    if data_table_count < chart_shell_count:
        errors.append(
            f"CHART GOVERNANCE: {chart_shell_count} chart cards/panels but only {data_table_count} corresponding data table containers — "
            "each chart must include its own default-hidden data table (`chart-data-table` / `data-table-panel` / modal)."
        )
    if hidden_table_count == 0:
        errors.append(
            "CHART GOVERNANCE: chart data tables are not default-hidden — "
            "actual data should be hidden initially and shown only after the user clicks `查看数据`."
        )
    if not re.search(r"(toggleChartData|openChartData|showChartData|data-table-modal)", content, re.IGNORECASE):
        errors.append(
            "CHART GOVERNANCE: missing data-table interaction handler — "
            "clicking `查看数据` must open/toggle the corresponding data table."
        )
    if not re.search(r"(统计口径|口径说明|chart-scope|data-scope)", content, re.IGNORECASE):
        errors.append(
            "CHART GOVERNANCE: missing chart-level statistical scope / 统计口径说明."
        )
    if not re.search(r"(数据来源|来源表|source table|chart-source|data-source|query hash)", content, re.IGNORECASE):
        errors.append(
            "CHART GOVERNANCE: missing chart-level data source / 数据来源 / query hash."
        )
    return errors


def _detect_dashboard_visual_layout_issues(content):
    errors = []
    errors.extend(_detect_narrow_fixed_layout(content))
    errors.extend(_detect_dashboard_grid_density_issues(content))
    errors.extend(_detect_chart_card_dimension_issues(content))
    errors.extend(_detect_long_table_without_scroll(content))
    errors.extend(_detect_card_text_wrap_issues(content))
    errors.extend(_detect_dense_cards_without_span(content))
    errors.extend(_detect_orphan_half_width_cards(content))
    errors.extend(_detect_first_dashboard_card_not_wide(content))
    errors.extend(_detect_span_class_css_issues(content))
    errors.extend(_detect_misapplied_full_width_grid_issues(content))
    return errors


def validate(html_path):
    with open(html_path) as f:
        content = f.read()

    errors = []
    warnings = []
    parsed_html = _parse_html(content)

    # ─────────────────────────────────────────────────────────────
    # 0. Script-tag integrity (MUST RUN FIRST — catches blank pages that
    #    HTMLParser-based checks below cannot see)
    # ─────────────────────────────────────────────────────────────
    errors.extend(_check_script_tag_integrity(content))

    # ─────────────────────────────────────────────────────────────
    # 0. Single File Compliance (catches most 404s)
    # ─────────────────────────────────────────────────────────────
    # 0a. External script src (not data: URI)
    external_scripts = re.findall(
        r'<script\s[^>]*src\s*=\s*["\'](?!data:)([^"\']+)["\']',
        content, re.IGNORECASE
    )
    if external_scripts:
        for src in external_scripts:
            errors.append(
                f"FORBIDDEN external script: src=\"{src[:120]}\" — "
                f"all JS must be inlined (Single File rule)"
            )

    # 0b. External stylesheet href (not data: URI)
    external_styles = re.findall(
        r'<link\s[^>]*href\s*=\s*["\'](?!data:)([^"\']+)["\']',
        content, re.IGNORECASE
    )
    if external_styles:
        for href in external_styles:
            errors.append(
                f"FORBIDDEN external stylesheet: href=\"{href[:120]}\" — "
                f"all CSS must be inlined (Single File rule)"
            )

    # 0c. Hardcoded localhost IP:port references (the #1 cause of 404 errors)
    hardcoded_urls = re.findall(
        r'(?:https?://)?(?:127\.0\.0\.1|localhost):\d{2,5}[^\s"\'<>]*',
        content
    )
    if hardcoded_urls:
        for url in hardcoded_urls:
            errors.append(
                f"FORBIDDEN hardcoded port URL: \"{url[:120]}\" — "
                f"ports are dynamic, use relative paths or inline everything"
            )

    # 0d. Runtime external loaders also break the Single File rule. These do not
    # appear as literal <script src> tags until the browser executes the page.
    dynamic_external_patterns = [
        (r"\.src\s*=\s*['\"]https?://", "runtime script/style src assignment"),
        (r"fetch\s*\(\s*['\"]https?://", "runtime fetch"),
        (r"innerHTML\s*\+?=\s*['\"][^'\"]*<script[^>]+src\s*=\s*['\"]https?://", "runtime injected script tag"),
    ]
    for pattern, label in dynamic_external_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            errors.append(
                f"FORBIDDEN external loader: {label} — "
                f"all runtime dependencies must be inlined for file:// dashboards"
            )

    # 0e. Invalid global assignment syntax seen in generated dashboards.
    if re.search(r"\bvar\s+window\.", content):
        errors.append(
            "INVALID JS: found `var window.*` — assign globals as `window.name = ...`"
        )

    if _chart_bootstrap_before_echarts(parsed_html):
        errors.append(
            "DASHBOARD: chart bootstrap appears before the inlined ECharts library — "
            "embed ECharts/map/html2canvas/jsPDF/dashboard assets first, then define and run chart bootstrap"
        )

    if "echarts.init" in content and not _has_inlined_echarts_library(parsed_html):
        errors.append(
            "MISSING: inlined ECharts library — generated chart/report/dashboard HTML must embed "
            "assets/echarts/echarts.min.js before any echarts.init call"
        )

    # 0f. Browser-free structural checks. Standalone chart/dashboard files should
    # not contain frames or file/http asset references. These are especially
    # fragile under file:// unique-origin rules.
    for tag, attrs in parsed_html.tags:
        if tag in ("iframe", "frame", "object", "embed"):
            errors.append(
                f"FORBIDDEN embedded frame/object: <{tag}> — "
                f"standalone dashboard HTML must not load itself or nested documents"
            )
        for attr_name in ("src", "href", "data", "poster"):
            attr_value = attrs.get(attr_name)
            if _unsafe_url(attr_value):
                errors.append(
                    f"FORBIDDEN URL asset on <{tag}>: {attr_name}=\"{attr_value[:120]}\" — "
                    f"inline the asset or remove the reference"
                )

    custom_scripts = _custom_inline_scripts(parsed_html)
    errors.extend(_detect_unbalanced_echarts_graphic_calls(custom_scripts))
    errors.extend(_detect_large_handwritten_data_objects(custom_scripts))
    errors.extend(_run_node_syntax_check(custom_scripts))

    # ─────────────────────────────────────────────────────────────
    # 1. ECharts init
    # ─────────────────────────────────────────────────────────────
    if "echarts.init" not in content:
        errors.append("MISSING: echarts.init — chart won't render")

    # ─────────────────────────────────────────────────────────────
    # 2. setOption
    # ─────────────────────────────────────────────────────────────
    if "setOption" not in content:
        errors.append("MISSING: setOption — no option applied")

    # ─────────────────────────────────────────────────────────────
    # 3. Unresolved placeholders
    # ─────────────────────────────────────────────────────────────
    unresolved = re.findall(r'\{\{[A-Z_]+\}\}', content)
    if unresolved:
        errors.append(f"UNRESOLVED placeholders: {unresolved}")

    has_report_chart_specs = "window.reportChartSpecs" in content
    report_chart_specs = _extract_report_chart_specs(content)
    stripped_content = _strip_js_comments(content)

    # ─────────────────────────────────────────────────────────────
    # 4. Series type present
    # ─────────────────────────────────────────────────────────────
    if has_report_chart_specs:
        types = _chart_types_from_specs(report_chart_specs)
    else:
        types = re.findall(r"['\"]?type['\"]?\s*:\s*['\"]([^'\"]+)['\"]", stripped_content)
    chart_types = [t for t in types if t in (
        'bar','line','pie','scatter','map','radar','funnel','gauge',
        'heatmap','treemap','sunburst','sankey','graph','tree','boxplot',
        'parallel','candlestick','pictorialBar','themeRiver','chord',
        'lines','effectScatter','bar3D','scatter3D','surface','line3D','custom'
    )]
    if not chart_types:
        errors.append("MISSING: no chart series type found")

    # ─────────────────────────────────────────────────────────────
    # 5. Data present
    # ─────────────────────────────────────────────────────────────
    if has_report_chart_specs:
        has_data = _specs_have_data(report_chart_specs)
    else:
        has_data = re.search(r"['\"]?data['\"]?\s*:\s*\[(?!\])", stripped_content) or \
                   re.search(r"['\"]?source['\"]?\s*:", stripped_content)
    if not has_data:
        errors.append("MISSING: no data in series/dataset")

    # ─────────────────────────────────────────────────────────────
    # 6. 3D charts need echarts-gl
    # ─────────────────────────────────────────────────────────────
    if any(t in ('bar3D','scatter3D','surface','line3D','lines3D') for t in chart_types):
        if "echarts-gl" not in content:
            errors.append("MISSING: echarts-gl not loaded for 3D chart")

    # ─────────────────────────────────────────────────────────────
    # 7. Map/geo charts need GeoJSON
    # ─────────────────────────────────────────────────────────────
    geo_or_map = any(t in ('map','lines','effectScatter') for t in chart_types) or \
                 ('geo' in content and 'coordinateSystem' in content)
    if geo_or_map:
        if "registerMap" not in content and "FeatureCollection" not in content:
            errors.append("MISSING: map GeoJSON not loaded (MAP_INLINE issue?)")

    errors.extend(_detect_missing_chart_governance_and_data_access(content, is_dashboard=False))

    # ─────────────────────────────────────────────────────────────
    # 8. Dashboard-specific checks
    # ─────────────────────────────────────────────────────────────
    is_dashboard = _looks_like_dashboard(content, html_path)
    if is_dashboard:
        if _detect_raw_page_layout(content):
            errors.append(
                "DASHBOARD: raw Page/SimplePageLayout-style chart stack detected — "
                "do not use any naked page generator output for enterprise dashboards. "
                "Author the dashboard from the .md workflow/template with CSS Grid, "
                "header, KPI cards, chart cards, hierarchy, and inlined ECharts assets."
            )

        required_layout_classes = [
            "dashboard-header",
            "dashboard-grid",
            "chart-card",
            "kpi-card",
        ]
        missing_layout = [
            class_name for class_name in required_layout_classes
            if not _has_html_class(content, class_name)
            and f".{class_name}" not in content
        ]
        if missing_layout:
            errors.append(
                f"DASHBOARD: missing enterprise layout structure {missing_layout} — "
                f"dashboards must use a designed CSS Grid layout with header, KPI cards, "
                f"and chart cards. Do not ship bare stacked charts."
            )

        errors.extend(_detect_dashboard_visual_layout_issues(content))

        # 8a. DashboardController must be defined (dashboard.js inlined)
        if "DashboardController" not in content or "class DashboardController" not in content:
            errors.append(
                "DASHBOARD: DashboardController class not found — "
                "dashboard.js must be inlined in the HTML"
            )

        # 8b. html2canvas must be present for PDF export
        if "html2canvas" not in content:
            errors.append(
                "DASHBOARD: html2canvas not found — "
                "must inline assets/dashboard/html2canvas.min.js for PDF export"
            )

        # 8c. jsPDF must be present for PDF export
        if "jsPDF" not in content:
            errors.append(
                "DASHBOARD: jsPDF not found — "
                "must inline assets/dashboard/jspdf.umd.min.js for PDF export"
            )

        # 8d. Dashboard CSS should be inlined (check for key class names)
        dashboard_css_markers = [
            'dashboard-container', 'dashboard-header', 'dashboard-toolbar',
            'chart-card', 'chart-card-header', 'toast-container'
        ]
        missing_css = [m for m in dashboard_css_markers
                       if f'.{m}' not in content and f'#{m}' not in content
                       and f'class="{m}"' not in content and f"class='{m}'" not in content]
        if len(missing_css) > 3:  # Most markers missing → CSS likely not inlined
            errors.append(
                f"DASHBOARD: dashboard CSS appears missing — "
                f"must inline assets/dashboard/dashboard.css"
            )

        # 8e. downloadChart function must be available
        if "downloadChart" not in content:
            errors.append(
                "DASHBOARD: downloadChart function not found — "
                "chart download buttons will fail"
            )

        # 8f. html2canvas cannot parse several modern CSS color functions.
        # Keep exported dashboards conservative so PDF export works offline.
        unsupported_pdf_css = [
            "color-mix(",
            "oklch(",
            "oklab(",
            "lab(",
            "lch(",
        ]
        found_pdf_css = [token for token in unsupported_pdf_css if token in content]
        if found_pdf_css:
            errors.append(
                f"DASHBOARD: PDF-incompatible CSS color functions found: {found_pdf_css} — "
                f"use hex/rgb/rgba variables so html2canvas PDF export works"
            )

        custom_script_text = "\n".join(custom_scripts)
        runtime_self_load_patterns = [
            (r"document\.location\.href\s*=", "document.location.href assignment"),
            (r"window\.location(?:\.href)?\s*=", "window.location assignment"),
            (r"(?<![\w.])location\.href\s*=", "location.href assignment"),
            (r"window\.open\s*\(", "window.open"),
            (r"createElement\s*\(\s*['\"]iframe['\"]\s*\)", "dynamic iframe creation"),
            (r"\.src\s*=\s*['\"]file://", "runtime file:// src assignment"),
            (r"\.href\s*=\s*['\"]file://", "runtime file:// href assignment"),
        ]
        for pattern, label in runtime_self_load_patterns:
            if re.search(pattern, custom_script_text, re.IGNORECASE):
                errors.append(
                    f"DASHBOARD: forbidden runtime navigation/self-load pattern: {label} — "
                    f"file:// dashboards must not navigate or create nested frames"
                )

        if "async exportDashboard" in content:
            export_match = re.search(
                r"async\s+exportDashboard\s*\([^)]*\)\s*\{",
                content,
            )
            if export_match:
                export_body = _extract_balanced(content, export_match.end() - 1, "{", "}")
                if "try" not in export_body or "catch" not in export_body:
                    errors.append(
                        "DASHBOARD: exportDashboard must catch PDF export errors and fallback to print"
                    )
                if "window.print" not in export_body:
                    errors.append(
                        "DASHBOARD: exportDashboard must include window.print() fallback"
                    )
                if "html2canvas" in export_body and "ignoreElements" not in export_body:
                    errors.append(
                        "DASHBOARD: exportDashboard uses html2canvas without ignoreElements — "
                        "toast/overlay nodes may leak into exported PDF and destabilize export"
                    )
                if (
                    re.search(r"new\s+jsPDF\s*\(", export_body)
                    and "window.jspdf" not in export_body
                    and "jspdf.jsPDF" not in export_body
                ):
                    errors.append(
                        "DASHBOARD: exportDashboard directly calls `new jsPDF(...)` — "
                        "resolve jsPDF via `window.jspdf.jsPDF || window.jsPDF` before creating the PDF"
                    )

    # ─────────────────────────────────────────────────────────────
    # 9. Warnings (non-fatal, but worth noting)
    # ─────────────────────────────────────────────────────────────
    # 9a. File is unusually small (likely missing inline libraries)
    if len(content) < 10000 and "echarts" not in content.lower():
        warnings.append(
            f"WARNING: file is very small ({len(content)} bytes) — "
            f"ECharts library may not be inlined"
        )

    # Report
    if errors or warnings:
        basename = os.path.basename(html_path)
        for w in warnings:
            print(f"⚠️  {basename}: {w}")
        for e in errors:
            print(f"❌ {basename}: {e}")
        if errors:
            return 1
        else:
            return 0  # warnings only = still valid
    else:
        print(f"✅ {os.path.basename(html_path)}: valid chart ({len(content)} bytes, types={chart_types})")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_chart.py <chart.html>")
        sys.exit(2)
    sys.exit(validate(sys.argv[1]))
