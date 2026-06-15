"""
Hard-check: validate generated chart HTML has renderable ECharts config.
Run after Agent generates a chart. Auto-detects and reports issues.
Usage: python scripts/validate_chart.py <path/to/chart.html>
Exit code 0 = valid, 1 = invalid (with error details)
"""
import re, sys, os, json


def validate(html_path):
    with open(html_path) as f:
        content = f.read()

    errors = []
    warnings = []

    # ─────────────────────────────────────────────────────────────
    # 0. Single File Compliance (MUST RUN FIRST — catches most 404s)
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

    # ─────────────────────────────────────────────────────────────
    # 4. Series type present
    # ─────────────────────────────────────────────────────────────
    types = re.findall(r"type:\s*['\"]([^'\"]+)['\"]", content)
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
    has_data = re.search(r"['\"]data['\"]\s*:\s*\[(?!\])", content) or \
               re.search(r"['\"]source['\"]\s*:", content)
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

    # ─────────────────────────────────────────────────────────────
    # 8. Dashboard-specific checks
    # ─────────────────────────────────────────────────────────────
    is_dashboard = bool(
        re.search(r'DashboardController|dashboard-container|dashboard-grid', content)
    )
    if is_dashboard:
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
