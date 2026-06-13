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

    # 1. ECharts init
    if "echarts.init" not in content:
        errors.append("MISSING: echarts.init — chart won't render")

    # 2. setOption
    if "setOption" not in content:
        errors.append("MISSING: setOption — no option applied")

    # 3. Unresolved placeholders
    unresolved = re.findall(r'\{\{[A-Z_]+\}\}', content)
    if unresolved:
        errors.append(f"UNRESOLVED placeholders: {unresolved}")

    # 4. Series type present
    types = re.findall(r"type:\s*['\"]([^'\"]+)['\"]", content)
    chart_types = [t for t in types if t in (
        'bar','line','pie','scatter','map','radar','funnel','gauge',
        'heatmap','treemap','sunburst','sankey','graph','tree','boxplot',
        'parallel','candlestick','pictorialBar','themeRiver','chord',
        'lines','effectScatter','bar3D','scatter3D','surface','line3D','custom'
    )]
    if not chart_types:
        errors.append("MISSING: no chart series type found")

    # 5. Data present
    has_data = re.search(r"['\"]data['\"]\s*:\s*\[(?!\])", content) or \
               re.search(r"['\"]source['\"]\s*:", content)
    if not has_data:
        errors.append("MISSING: no data in series/dataset")

    # 6. 3D charts need echarts-gl
    if any(t in ('bar3D','scatter3D','surface','line3D','lines3D') for t in chart_types):
        if "echarts-gl" not in content:
            errors.append("MISSING: echarts-gl not loaded for 3D chart")

    # 7. Map/geo charts need GeoJSON
    geo_or_map = any(t in ('map','lines','effectScatter') for t in chart_types) or \
                 ('geo' in content and 'coordinateSystem' in content)
    if geo_or_map:
        if "registerMap" not in content and "FeatureCollection" not in content:
            errors.append("MISSING: map GeoJSON not loaded (MAP_INLINE issue?)")

    # Report
    if errors:
        print(f"❌ {os.path.basename(html_path)}: {'; '.join(errors)}")
        return 1
    else:
        print(f"✅ {os.path.basename(html_path)}: valid chart ({len(content)} bytes, types={chart_types})")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_chart.py <chart.html>")
        sys.exit(2)
    sys.exit(validate(sys.argv[1]))
