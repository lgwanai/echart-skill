import argparse
import asyncio
import html as html_mod
import json
import os
import io
import urllib.request
import urllib.parse
import copy
import sys
from typing import Optional

import httpx
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_repository
from logging_config import get_logger, configure_logging
from scripts.server import ensure_server_running

# Initialize logging
configure_logging()
logger = get_logger(__name__)

# Async geocoding configuration
MAX_CONCURRENT_GEOCODING = 5
GEOCODING_TIMEOUT = 10.0

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


class AsyncGeocoder:
    """Async geocoding client with caching and retry logic.

    Provides concurrent batch geocoding with:
    - Semaphore-based concurrency control (max 5 concurrent)
    - Automatic retry with exponential backoff (3 attempts)
    - Cache integration for deduplication
    """

    def __init__(self, ak: str, cache_path: str):
        """Initialize the async geocoder.

        Args:
            ak: Baidu API key
            cache_path: Path to the cache JSON file
        """
        self._ak = ak
        self._cache_path = cache_path
        self._cache = self._load_cache()

    def _load_cache(self) -> dict:
        """Load geocoding cache from file."""
        if os.path.exists(self._cache_path):
            try:
                with open(self._cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_cache(self) -> None:
        """Save geocoding cache to file."""
        os.makedirs(os.path.dirname(self._cache_path), exist_ok=True)
        with open(self._cache_path, 'w', encoding='utf-8') as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=4)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True
    )
    async def _geocode_single(
        self,
        client: httpx.AsyncClient,
        address: str
    ) -> Optional[list[float]]:
        """Geocode a single address with retry logic.

        Args:
            client: Async HTTP client
            address: Address to geocode

        Returns:
            [lng, lat] coordinates or None if geocoding failed

        Raises:
            httpx.HTTPStatusError: On HTTP errors (triggers retry)
        """
        url = (
            f"https://api.map.baidu.com/geocoding/v3/"
            f"?address={urllib.parse.quote(address)}"
            f"&output=json&ak={self._ak}"
        )

        response = await client.get(url)

        # Raise on HTTP errors to trigger retry
        response.raise_for_status()

        res = response.json()

        if res.get('status') == 0 and 'result' in res and 'location' in res['result']:
            location = res['result']['location']
            return [location['lng'], location['lat']]

        return None

    async def geocode_batch(
        self,
        addresses: list[str]
    ) -> dict[str, Optional[list[float]]]:
        """Geocode multiple addresses concurrently.

        Args:
            addresses: List of addresses to geocode

        Returns:
            Dict mapping addresses to coordinates (or None for failures)
        """
        results: dict[str, Optional[list[float]]] = {}
        addresses_to_fetch = []

        # Check cache first
        for address in addresses:
            if address in self._cache:
                results[address] = self._cache[address]
            else:
                addresses_to_fetch.append(address)

        if not addresses_to_fetch:
            return results

        # Fetch uncached addresses concurrently
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_GEOCODING)

        async def fetch_with_semaphore(
            client: httpx.AsyncClient,
            address: str
        ) -> tuple[str, Optional[list[float]]]:
            async with semaphore:
                try:
                    coord = await self._geocode_single(client, address)
                    return (address, coord)
                except Exception as e:
                    logger.error("地理编码失败", address=address, error=str(e))
                    return (address, None)

        async with httpx.AsyncClient(timeout=GEOCODING_TIMEOUT) as client:
            tasks = [
                fetch_with_semaphore(client, addr)
                for addr in addresses_to_fetch
            ]
            fetch_results = await asyncio.gather(*tasks)

        # Process results and update cache
        for address, coord in fetch_results:
            results[address] = coord
            if coord is not None:
                self._cache[address] = coord

        # Save updated cache
        self._save_cache()

        return results


def get_geo_coord_batch(
    addresses: list[str],
    ak: str,
    cache_path: Optional[str] = None
) -> dict[str, Optional[list[float]]]:
    """Synchronous wrapper for batch geocoding.

    Args:
        addresses: List of addresses to geocode
        ak: Baidu API key
        cache_path: Path to cache file (defaults to references/geo_cache.json)

    Returns:
        Dict mapping addresses to coordinates (or None for failures)
    """
    if cache_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cache_path = os.path.join(base_dir, 'references', 'geo_cache.json')

    geocoder = AsyncGeocoder(ak, cache_path)
    return asyncio.run(geocoder.geocode_batch(addresses))

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
    
    title_escaped = html_mod.escape(title)
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title_escaped}</title>
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


def export_standalone_chart(config: dict, output_path: str, theme: str = "default") -> str:
    """Export chart as standalone HTML file with embedded scripts.
    
    Generates a self-contained HTML file that can be shared and viewed
    offline without any server or database connection.
    
    Args:
        config: Chart configuration dict with:
            - db_path: Path to database
            - query: SQL query for data
            - title: Chart title
            - echarts_option: ECharts option dict
            - custom_js: Optional custom JavaScript
        output_path: Output HTML file path
        theme: ECharts theme (default, dark, etc.)
        
    Returns:
        Path to generated HTML file
        
    Example:
        config = {
            "db_path": "workspace.duckdb",
            "query": "SELECT category, value FROM sales",
            "title": "Sales by Category",
            "echarts_option": {"xAxis": {"type": "category"}, "series": [{"type": "bar"}]}
        }
        export_standalone_chart(config, "sales_chart.html")
    """
    from scripts.html_exporter import HTMLExporter
    
    db_path = config.get("db_path", "workspace.duckdb")
    query = config.get("query")
    
    if not query:
        raise ValueError("Missing SQL query in config")
    
    repo = get_repository(db_path)
    with repo.connection() as conn:
        df = pd.read_sql_query(query, conn)
    
    if df.empty:
        logger.warning("Query returned empty data", query=query)
    
    option = config.get("echarts_option", {})
    if not option.get('dataset') and not df.empty:
        option['dataset'] = {'source': [df.columns.tolist()] + df.values.tolist()}
    
    option_json = json.dumps(option, ensure_ascii=False)
    data_json = json.dumps(df.to_dict(orient='records'), ensure_ascii=False)
    custom_js = config.get("custom_js", "")
    
    exporter = HTMLExporter()
    html = exporter.generate_standalone_html(
        title=config.get("title", "Chart"),
        option_json=option_json,
        data_json=data_json,
        custom_js=custom_js,
        theme=theme
    )
    
    logger.info(
        "Chart exported as standalone HTML",
        output_path=output_path,
        theme=theme,
        rows=len(df)
    )
    
    return exporter.export_to_file(html, output_path)


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

    # 1. 提取数据 - Use DatabaseRepository for connection pooling and WAL mode
    repo = get_repository(db_path)
    with repo.connection() as conn:
        df = pd.read_sql_query(query, conn)
    
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

if __name__ == "__main__":  # pragma: no cover
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
