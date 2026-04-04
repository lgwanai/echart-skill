import argparse
import sqlite3
import pandas as pd
import json
import os
import io
import urllib.request
import urllib.parse
import copy
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_config import get_logger, configure_logging
from server import ensure_server_running

# Initialize logging
configure_logging()
logger = get_logger(__name__)

def get_baidu_ak():
    """
    Retrieve Baidu AK from environment variable.
    config.txt support is DEPRECATED and will be removed.

    Priority:
    1. BAIDU_AK environment variable
    2. config.txt (deprecated, shows warning)
    """
    import warnings

    # Primary: environment variable
    ak = os.environ.get('BAIDU_AK')
    if ak:
        return ak

    # Fallback: config.txt (DEPRECATED)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config.txt')

    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('BAIDU_AK='):
                    ak = line.strip().split('=', 1)[1]
                    if ak:
                        warnings.warn(
                            "从 config.txt 读取 BAIDU_AK 已弃用，请设置环境变量 BAIDU_AK",
                            DeprecationWarning,
                            stacklevel=2
                        )
                        return ak

    # If not found or empty
    logger.warning(
        "使用 ECharts 地图功能需要百度地图 AK",
        action="请设置环境变量 BAIDU_AK",
        url="https://lbsyun.baidu.com/apiconsole/key"
    )
    return None

def get_geo_coord(address, ak):
    """Dynamically geocode address using Baidu API and cache the result."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_file = os.path.join(base_dir, 'references', 'geo_cache.json')
    cache = {}
    
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except Exception:
            pass
            
    if address in cache:
        return cache[address]
        
    url = f"https://api.map.baidu.com/geocoding/v3/?address={urllib.parse.quote(address)}&output=json&ak={ak}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            if res.get('status') == 0 and 'result' in res and 'location' in res['result']:
                location = res['result']['location']
                coord = [location['lng'], location['lat']]
                cache[address] = coord
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, ensure_ascii=False, indent=4)
                return coord
    except Exception as e:
        logger.error("地理编码失败", address=address, error=str(e))

    return None

def replace_placeholders(obj, replacements):
    """Recursively replace placeholders like {title} in the option dictionary."""
    if isinstance(obj, dict):
        return {k: replace_placeholders(v, replacements) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_placeholders(i, replacements) for i in obj]
    elif isinstance(obj, str):
        for k, v in replacements.items():
            if obj == f"{{{k}}}":
                return v
        for k, v in replacements.items():
            obj = obj.replace(f"{{{k}}}", str(v))
        return obj
    return obj

def generate_echarts_html(df, config, output_path):
    """Generate an interactive HTML file using ECharts configuration directly."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    baidu_ak = get_baidu_ak()
    bmap_script = ""
    
    title = config.get("title", "Chart")
    custom_js = config.get("custom_js", "")
    option = config.get("echarts_option", {})
    
    # 1. Automatic Dataset Injection (if not already provided by custom option)
    if not option.get('dataset') and not df.empty:
        # Check if custom_js relies heavily on rawData, if so we provide it
        dataset_source = [df.columns.tolist()] + df.values.tolist()
        option['dataset'] = {'source': dataset_source}
    
    raw_data_json = json.dumps(df.to_dict(orient='records'), ensure_ascii=False)
    # Expose rawData and datasetSource to JS scope for complex scripts
    dataset_source_json = json.dumps([df.columns.tolist()] + df.values.tolist(), ensure_ascii=False)
    custom_js = f"var rawData = {raw_data_json};\nvar datasetSource = {dataset_source_json};\n" + custom_js

    # Get server base url first to construct absolute paths for local assets
    base_url = ensure_server_running()

    # 2. BMap script injection check
    if ("bmap" in json.dumps(option) or "bmap" in custom_js) and baidu_ak:
        bmap_script = f"""
        <script type="text/javascript" src="https://api.map.baidu.com/api?v=3.0&ak={baidu_ak}"></script>
        <script src="{base_url}/assets/echarts/bmap.min.js"></script>
        """
    option_json = json.dumps(option, ensure_ascii=False)
    
    # 自动检测是否使用了 'china' 地图并注入 china.js
    china_map_script = ""
    if "china" in option_json or "china" in custom_js or "中国" in option_json or "中国" in custom_js:
        china_map_script = f'<script src="{base_url}/assets/echarts/china.js"></script>'
        
    # 自动检测是否使用了 'world' 地图并注入 world.js
    world_map_script = ""
    if "world" in option_json or "world" in custom_js or "世界" in option_json or "世界" in custom_js:
        world_map_script = f'<script src="{base_url}/assets/echarts/world.js"></script>'
    
    # 自动检测是否使用了各省市地图并注入对应的 js (如果有)
    province_map_scripts = []
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
    
    for cn_name, pinyin in province_pinyin_map.items():
        if cn_name in option_json or cn_name in custom_js or pinyin in custom_js:
            province_map_scripts.append(f'<script src="{base_url}/assets/echarts/{pinyin}.js"></script>')
            
    province_scripts_html = "\n        ".join(province_map_scripts)
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <script src="{base_url}/assets/echarts/echarts.min.js"></script>
        {bmap_script}
        {china_map_script}
        {world_map_script}
        {province_scripts_html}
    </head>
    <body>
        <div id="main" style="width: 100%; height: 800px;"></div>
        <script type="text/javascript">
            var myChart = echarts.init(document.getElementById('main'));
            var option = {option_json};
            
            {custom_js}
            
            myChart.setOption(option);
            window.addEventListener('resize', function() {{
                myChart.resize();
            }});
        </script>
    </body>
    </html>
    """
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with io.open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    rel_path = os.path.relpath(output_path, base_dir).replace(os.sep, '/')
    access_url = f"{base_url}/{rel_path}"

    logger.info(
        "ECharts 图表已生成",
        output_path=output_path,
        access_url=access_url,
        rows=len(df)
    )
    return output_path

def generate_chart(config):
    """
    Universal Chart Generator
    config = {
        "db_path": "workspace.db",
        "query": "SELECT category, SUM(value) as val FROM table GROUP BY category",
        "chart_type": "bar" | "pie" | "line" | "scatter" | "map",
        "x_col": "category", 
        "y_col": "val",      
        "title": "图表标题",
        "xlabel": "X轴标签",
        "ylabel": "Y轴标签",
        "output_path": "tmp/chart.html", 
        "show_labels": True 
    }
    """
    db_path = config.get("db_path", "workspace.db")
    query = config.get("query")
    
    if not query:
        raise ValueError("Missing SQL query in config")
        
    # 1. 提取数据
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        logger.warning("查询返回空数据", query=query)
        return None

    logger.info("数据查询成功", rows=len(df))
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_output = os.path.join(base_dir, "outputs", "html", "chart.html")
    output_path = config.get("output_path", default_output)
    if not output_path.endswith('.html'):
        output_path = os.path.splitext(output_path)[0] + '.html'
        
    return generate_echarts_html(df, config, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Chart Generator from SQLite")
    parser.add_argument("--config", required=True, help="JSON string or path to JSON file containing chart configuration")
    
    args = parser.parse_args()
    
    try:
        if os.path.isfile(args.config):
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = json.loads(args.config)
            
        generate_chart(config)
    except Exception as e:
        logger.error("图表生成失败", error=str(e), config=config if 'config' in dir() else None)
