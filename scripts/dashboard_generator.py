"""
Dashboard Generator.

Generates multi-chart HTML dashboards with CSS Grid layout.

Features:
- Load dashboard configuration from JSON file
- Fetch data for each chart from SQLite database
- Aggregate map scripts from all charts
- Generate single HTML with CSS Grid layout
- CLI interface with --config and --output flags

Usage:
    python scripts/dashboard_generator.py --config dashboard_config.json --output output.html
"""
import argparse
import json
import os
import sys

import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_repository
from logging_config import get_logger, configure_logging
from scripts.server import ensure_server_running
from scripts.chart_generator import get_baidu_ak
from scripts.dashboard_schema import DashboardConfig, ChartConfig, get_dashboard_json_schema

# Initialize logging
configure_logging()
logger = get_logger(__name__)


def load_dashboard_config(config_path: str) -> DashboardConfig:
    """Load and validate dashboard configuration from JSON file.

    Args:
        config_path: Path to JSON configuration file.

    Returns:
        Validated DashboardConfig object.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If config validation fails.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    try:
        config = DashboardConfig(**config_data)
        logger.info("Dashboard config loaded", title=config.title, charts=len(config.charts))
        return config
    except Exception as e:
        logger.error("Config validation failed", error=str(e))
        raise ValueError(f"Invalid dashboard config: {e}")


def fetch_chart_data(chart: ChartConfig, db_path: str) -> pd.DataFrame:
    """Fetch data for a chart from the database.

    Args:
        chart: Chart configuration.
        db_path: Path to SQLite database.

    Returns:
        DataFrame with query results (may be empty).
    """
    repo = get_repository(db_path)
    with repo.connection() as conn:
        df = pd.read_sql_query(chart.query, conn)

    if df.empty:
        logger.warning("Query returned empty result", chart_id=chart.id, query=chart.query)

    return df


def aggregate_map_scripts(
    charts: list[ChartConfig],
    option_jsons: list[str],
    base_url: str
) -> tuple[str, str, str, str]:
    """Aggregate map scripts from all charts.

    Scans all echarts_option and custom_js for map usage and returns
    the necessary script tags.

    Args:
        charts: List of chart configurations.
        option_jsons: List of JSON-serialized echarts options.
        base_url: Base URL for local asset paths.

    Returns:
        Tuple of (bmap_script, china_script, world_script, province_scripts).
    """
    baidu_ak = get_baidu_ak()
    bmap_script = ""
    china_script = ""
    world_script = ""
    province_scripts = []

    # Province name to pinyin mapping (same as chart_generator.py)
    province_pinyin_map = {
        "安徽": "anhui", "澳门": "aomen", "北京": "beijing", "重庆": "chongqing",
        "福建": "fujian", "甘肃": "gansu", "广东": "guangdong", "广西": "guangxi",
        "贵州": "guizhou", "海南": "hainan", "河北": "hebei", "黑龙江": "heilongjiang",
        "河南": "henan", "湖北": "hubei", "湖南": "hunan", "江苏": "jiangsu",
        "江西": "jiangxi", "吉林": "jilin", "辽宁": "liaoning", "内蒙古": "neimenggu",
        "宁夏": "ningxia", "青海": "qinghai", "山东": "shandong", "上海": "shanghai",
        "山西": "shanxi", "陕西": "shanxi1", "四川": "sichuan", "台湾": "taiwan",
        "天津": "tianjin", "香港": "xianggang", "新疆": "xinjiang", "西藏": "xizang",
        "云南": "yunnan", "浙江": "zhejiang"
    }

    # Combine all JSON strings for scanning
    all_json = " ".join(option_jsons)
    all_custom_js = " ".join(chart.custom_js for chart in charts)

    # Check for BMap
    if ("bmap" in all_json or "bmap" in all_custom_js) and baidu_ak:
        bmap_script = f"""
        <script type="text/javascript" src="https://api.map.baidu.com/api?v=3.0&ak={baidu_ak}"></script>
        <script src="{base_url}/assets/echarts/bmap.min.js"></script>
        """

    # Check for china map
    if "china" in all_json or "china" in all_custom_js or "中国" in all_json or "中国" in all_custom_js:
        china_script = f'<script src="{base_url}/assets/echarts/china.js"></script>'

    # Check for world map
    if "world" in all_json or "world" in all_custom_js or "世界" in all_json or "世界" in all_custom_js:
        world_script = f'<script src="{base_url}/assets/echarts/world.js"></script>'

    # Check for province maps
    for cn_name, pinyin in province_pinyin_map.items():
        if cn_name in all_json or cn_name in all_custom_js or pinyin in all_custom_js:
            province_scripts.append(f'<script src="{base_url}/assets/echarts/{pinyin}.js"></script>')

    province_scripts_str = "\n        ".join(province_scripts)

    return bmap_script, china_script, world_script, province_scripts_str


def generate_dashboard_html(config: DashboardConfig, output_path: str) -> str:
    """Generate HTML file with dashboard containing all charts.

    Creates a single HTML file with professional UI/UX design including:
    - Modern card-based layout
    - Dark/Light theme toggle
    - Responsive grid layout
    - Interactive features (refresh, export, filters)
    - Auto-refresh capability

    Args:
        config: Validated dashboard configuration.
        output_path: Path to write HTML output.

    Returns:
        Path to generated HTML file.
    """
    base_url = ensure_server_running()
    
    # Ensure dashboard assets directory exists
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dashboard_assets_dir = os.path.join(base_dir, 'assets', 'dashboard')
    os.makedirs(dashboard_assets_dir, exist_ok=True)
    
    # Link dashboard CSS and JS
    dashboard_css_path = os.path.join(dashboard_assets_dir, 'dashboard.css')
    dashboard_js_path = os.path.join(dashboard_assets_dir, 'dashboard.js')
    
    # Use embedded CSS/JS if files don't exist (fallback)
    dashboard_css_url = f"{base_url}/assets/dashboard/dashboard.css"
    dashboard_js_url = f"{base_url}/assets/dashboard/dashboard.js"

    # Collect chart initialization scripts
    chart_inits = []
    option_jsons = []
    chart_cards = []

    for chart in config.charts:
        # Fetch data
        df = fetch_chart_data(chart, config.db_path)

        # Build echarts option
        option = chart.echarts_option.copy()

        # Inject dataset if not provided and df not empty
        if not option.get('dataset') and not df.empty:
            dataset_source = [df.columns.tolist()] + df.values.tolist()
            option['dataset'] = {'source': dataset_source}

        # Prepare custom JS with rawData
        raw_data_json = json.dumps(df.to_dict(orient='records'), ensure_ascii=False)
        dataset_source_json = json.dumps([df.columns.tolist()] + df.values.tolist(), ensure_ascii=False)
        custom_js = f"var rawData = {raw_data_json};\nvar datasetSource = {dataset_source_json};\n" + chart.custom_js

        option_json = json.dumps(option, ensure_ascii=False)
        option_jsons.append(option_json)

        # Build chart card HTML
        pos = chart.position
        chart_card = f"""        <div class="chart-card" style="grid-row: {pos.row + 1} / span {pos.row_span}; grid-column: {pos.col + 1} / span {pos.col_span};">
            <div class="chart-card-header">
                <h3 class="chart-card-title">{chart.title}</h3>
                <div class="chart-card-actions">
                    <button class="btn btn-icon btn-ghost" onclick="dashboard.downloadChart('{chart.id}', '{chart.title}.png')" title="Download">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M10 12l-4-4h3V3h2v5h3l-4 4zm-7 5v-2h14v2H3z"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="chart-card-body">
                <div id="chart_{chart.id}" class="chart-container"></div>
            </div>
        </div>"""
        chart_cards.append(chart_card)

        # Build chart init script
        chart_init = f"""
    (function() {{
        var chart = echarts.init(document.getElementById('chart_{chart.id}'));
        var option = {option_json};
        {custom_js}
        chart.setOption(option);
        charts.push(chart);
    }})();
"""
        chart_inits.append(chart_init)

    chart_cards_html = "\n".join(chart_cards)
    chart_inits_html = "\n".join(chart_inits)

    # Aggregate map scripts
    bmap_script, china_script, world_script, province_scripts = aggregate_map_scripts(
        config.charts, option_jsons, base_url
    )

    # Build HTML template
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.title}</title>
    <link rel="stylesheet" href="{dashboard_css_url}">
    <style>
        :root {{
            --grid-columns: {config.columns};
            --row-height: {config.row_height}px;
        }}
    </style>
    <script src="{base_url}/assets/echarts/echarts.min.js"></script>
    {bmap_script}
    {china_script}
    {world_script}
    {province_scripts}
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <header class="dashboard-header">
            <div class="header-content">
                <h1 class="dashboard-title">
                    <svg class="dashboard-title-icon" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M3 13h8v8H3v-8zm0-10h8v8H3V3zm10 0h8v8h-8V3zm0 10h8v8h-8v-8z"/>
                    </svg>
                    {config.title}
                </h1>
                <div class="header-actions">
                    <span id="dashboard-timestamp" class="header-timestamp">Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                    <button id="theme-toggle" class="btn btn-ghost btn-icon" title="Toggle Theme">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 01-6-6 6 6 0 016-6V2z"/>
                        </svg>
                    </button>
                </div>
            </div>
        </header>

        <!-- Toolbar -->
        <div class="dashboard-toolbar">
            <div class="toolbar-content">
                <div class="toolbar-filters">
                    <input type="text" id="chart-filter" class="form-input" placeholder="Search charts..." style="padding: 8px 12px; border: 1px solid var(--border-color); border-radius: 6px; width: 200px;">
                </div>
                <div class="toolbar-actions">
                    <button id="refresh-dashboard" class="btn btn-secondary">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M13.65 2.35A8 8 0 102.35 13.65 8 8 0 0013.65 2.35zM8 14A6 6 0 118 2a6 6 0 010 12z"/>
                            <path d="M7 4h2v4.5l3 1.5-.75 1.5L7 9.5V4z"/>
                        </svg>
                        Refresh
                    </button>
                    <button id="export-dashboard" class="btn btn-primary">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M14 12v2H2v-2h12zm0-6v2H2V6h12zm0-6v2H2V0h12z"/>
                        </svg>
                        Export PDF
                    </button>
                </div>
            </div>
        </div>

        <!-- Dashboard Body -->
        <main class="dashboard-body">
            <div class="dashboard-grid" style="--grid-columns: {config.columns}; --row-height: {config.row_height}px;">
{chart_cards_html}
            </div>
        </main>

        <!-- Toast Container -->
        <div id="toast-container" class="toast-container"></div>

        <!-- Loading Overlay -->
        <div id="loading-overlay" class="loading-overlay visually-hidden">
            <div class="spinner"></div>
        </div>
    </div>

    <script>
        var charts = [];
{chart_inits_html}

        // Initialize dashboard controller
        var dashboard = new DashboardController({{
            charts: charts,
            config: {{
                title: '{config.title}',
                autoRefreshInterval: 30000
            }}
        }});

        // Chart filter
        document.getElementById('chart-filter').addEventListener('input', function(e) {{
            dashboard.filterCharts(e.target.value);
        }});
    </script>
    <script src="{dashboard_js_url}"></script>
</body>
</html>"""

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    rel_path = os.path.relpath(output_path, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    access_url = f"{base_url}/{rel_path}"

    logger.info(
        "Dashboard HTML generated",
        output_path=output_path,
        access_url=access_url,
        charts=len(config.charts)
    )

    return output_path


def export_standalone_dashboard(config_path: str, output_path: str, theme: str = "default") -> str:
    """Export dashboard as standalone HTML file with embedded scripts.
    
    Generates a self-contained HTML file with all chart data and ECharts
    library embedded, suitable for offline sharing.
    
    Args:
        config_path: Path to dashboard configuration JSON file
        output_path: Output HTML file path
        theme: ECharts theme (default, dark, etc.)
        
    Returns:
        Path to generated HTML file
    """
    from scripts.html_exporter import HTMLExporter
    
    config = load_dashboard_config(config_path)
    
    chart_inits = []
    required_maps = set()
    
    exporter = HTMLExporter()
    
    for chart in config.charts:
        df = fetch_chart_data(chart, config.db_path)
        
        option = chart.echarts_option.copy()
        if not option.get('dataset') and not df.empty:
            option['dataset'] = {'source': [df.columns.tolist()] + df.values.tolist()}
        
        option_json = json.dumps(option, ensure_ascii=False)
        data_json = json.dumps(df.to_dict(orient='records'), ensure_ascii=False)
        dataset_json = json.dumps([df.columns.tolist()] + df.values.tolist(), ensure_ascii=False)
        
        custom_js = f"var rawData = {data_json};\nvar datasetSource = {dataset_json};\n" + chart.custom_js
        
        maps = exporter._detect_required_maps(option_json, custom_js)
        required_maps.update(maps)
        
        chart_init = f"""    (function() {{
        var chart = echarts.init(document.getElementById('chart_{chart.id}'));
        var option = {option_json};
        {custom_js}
        chart.setOption(option);
        charts.push(chart);
    }})();"""
        chart_inits.append(chart_init)
    
    echarts_content = exporter._load_echarts()
    map_scripts = "\n".join(exporter._load_map_script(m) for m in required_maps)
    chart_inits_js = "\n".join(chart_inits)
    
    containers = []
    for chart in config.charts:
        pos = chart.position
        containers.append(
            f'<div id="chart_{chart.id}" style="grid-row: {pos.row + 1} / span {pos.row_span}; '
            f'grid-column: {pos.col + 1} / span {pos.col_span};"></div>'
        )
    
    theme_style = ""
    if theme == "dark":
        theme_style = "body { background-color: #1a1a1a; }"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{config.title}</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat({config.columns}, 1fr);
            grid-auto-rows: {config.row_height}px;
            gap: {config.gap}px;
            padding: 16px;
        }}
        .chart-container {{ min-height: {config.row_height}px; border: 1px solid #ddd; border-radius: 4px; }}
        {theme_style}
    </style>
</head>
<body>
    <div class="dashboard-grid">
{chr(10).join('        ' + c for c in containers)}
    </div>
    <script>
{echarts_content}
    </script>
    <script>
{map_scripts}
    </script>
    <script>
        var charts = [];
{chart_inits_js}
        window.addEventListener('resize', function() {{
            charts.forEach(function(c) {{ c.resize(); }});
        }});
    </script>
</body>
</html>"""
    
    logger.info(
        "Dashboard exported as standalone HTML",
        output_path=output_path,
        theme=theme,
        charts=len(config.charts)
    )
    
    return exporter.export_to_file(html, output_path)


def generate_dashboard(config_path: str, output_path: str | None = None) -> str:
    """Generate dashboard from configuration file.

    Main entry point for dashboard generation.

    Args:
        config_path: Path to JSON configuration file.
        output_path: Optional output path. Defaults to outputs/html/dashboards/{title}.html.

    Returns:
        Path to generated HTML file.
    """
    config = load_dashboard_config(config_path)

    if output_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_dir, "outputs", "html", "dashboards", f"{config.title}.html")

    return generate_dashboard_html(config, output_path)


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(description="Dashboard Generator")
    parser.add_argument("--config", required=True, help="Path to dashboard configuration JSON file")
    parser.add_argument("--output", help="Output HTML file path (optional)")

    args = parser.parse_args()

    try:
        result_path = generate_dashboard(args.config, args.output)
        print(f"Dashboard generated: {result_path}")
    except Exception as e:
        logger.error("Dashboard generation failed", error=str(e))
        sys.exit(1)
