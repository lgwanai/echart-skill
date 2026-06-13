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
from scripts.config_manager import get_config
from scripts.html_exporter import HTMLExporter
from scripts.server import ensure_server_running

# Initialize logging
configure_logging()
logger = get_logger(__name__)

# Async geocoding configuration
MAX_CONCURRENT_GEOCODING = 5
GEOCODING_TIMEOUT = 10.0

# ---------------------------------------------------------------------------
# Map name normalization
# ---------------------------------------------------------------------------
# The ECharts china.js / world.js map files use canonical names that may
# differ from the names produced by SQL queries or LLM-generated data.
# This table maps common variations to the canonical form expected by the map.
NAME_NORMALIZATION_MAP: dict[str, str] = {
    # Provincial-level: full name → canonical short name
    "北京市": "北京",
    "上海市": "上海",
    "天津市": "天津",
    "重庆市": "重庆",
    "河北省": "河北",
    "山西省": "山西",
    "辽宁省": "辽宁",
    "吉林省": "吉林",
    "黑龙江省": "黑龙江",
    "江苏省": "江苏",
    "浙江省": "浙江",
    "安徽省": "安徽",
    "福建省": "福建",
    "江西省": "江西",
    "山东省": "山东",
    "河南省": "河南",
    "湖北省": "湖北",
    "湖南省": "湖南",
    "广东省": "广东",
    "广西壮族自治区": "广西",
    "海南省": "海南",
    "四川省": "四川",
    "贵州省": "贵州",
    "云南省": "云南",
    "西藏自治区": "西藏",
    "陕西省": "陕西",
    "甘肃省": "甘肃",
    "青海省": "青海",
    "宁夏回族自治区": "宁夏",
    "新疆维吾尔自治区": "新疆",
    "内蒙古自治区": "内蒙古",
    "台湾省": "台湾",
    "香港特别行政区": "香港",
    "澳门特别行政区": "澳门",
}


def normalize_map_name(name: str) -> str:
    """Normalize a region name to its canonical map form.

    Strips common suffixes ("省", "市", "自治区", "特别行政区") and
    consults a lookup table for known variations.

    Args:
        name: Raw region name from data (e.g. "北京市", "广东省")

    Returns:
        Canonical name expected by the map GeoJSON (e.g. "北京", "广东")
    """
    if not name or not isinstance(name, str):
        return name

    # Check exact-match lookup table first
    if name in NAME_NORMALIZATION_MAP:
        return NAME_NORMALIZATION_MAP[name]

    # Generic suffix stripping (order matters: longer suffixes first)
    suffixes = [
        "维吾尔自治区", "壮族自治区", "回族自治区", "特别行政区",
        "自治区", "省", "市",
    ]
    result = name
    for suffix in suffixes:
        if result.endswith(suffix) and len(result) > len(suffix):
            result = result[: -len(suffix)]
            break

    return result


def normalize_map_data(data: list, name_key: str = "name") -> list:
    """Normalize region names in a list of map data items.

    Args:
        data: List of dicts with a ``name`` field (e.g. ``[{name: "北京市", value: 100}]``)
        name_key: The key in each dict that holds the region name

    Returns:
        New list with normalized names. Items without the name_key are passed
        through unchanged.
    """
    normalized = []
    for item in data:
        if isinstance(item, dict) and name_key in item:
            original = item[name_key]
            new_name = normalize_map_name(original)
            if new_name != original:
                logger.debug(
                    "地图名称已标准化",
                    original=original,
                    normalized=new_name,
                )
            item = {**item, name_key: new_name}
        normalized.append(item)
    return normalized


def get_baidu_ak():
    """
    Retrieve Baidu AK from environment, echart_config.txt, or legacy config.txt.

    Priority:
    1. BAIDU_AK environment variable
    2. echart_config.txt baidu_ak field
    3. config.txt (deprecated, shows warning)
    """
    import warnings

    # Primary: environment variable
    ak = os.environ.get('BAIDU_AK')
    if ak:
        return ak

    # Secondary: echart_config.txt
    try:
        cfg = get_config()
        if cfg.baidu_ak:
            return cfg.baidu_ak
    except Exception:
        pass

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
                            "从 config.txt 读取 BAIDU_AK 已弃用，请设置环境变量 BAIDU_AK 或在 echart_config.txt 中配置",
                            DeprecationWarning,
                            stacklevel=2
                        )
                        return ak

    # If not found or empty
    logger.warning(
        "使用 ECharts 地图功能需要百度地图 AK",
        action="请设置环境变量 BAIDU_AK 或在 echart_config.txt 中配置 baidu_ak",
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


def _is_map_chart(option: dict, custom_js: str) -> bool:
    """Detect if the current chart config is for a map-type visualization.

    Checks both the ECharts option's series types and typical map-related
    keywords in the custom JS.
    """
    combined = json.dumps(option, ensure_ascii=False) + custom_js

    # Check series types
    for series in option.get("series", []):
        if series.get("type") in ("map", "geo"):
            return True
        # scatter/effectScatter with geo/bmap coordinateSystem
        if series.get("type") in ("scatter", "effectScatter") and \
           series.get("coordinateSystem") in ("geo", "bmap"):
            return True

    # Keyword fallback
    map_keywords = ["map", "china", "world", "geo", "bmap"]
    return any(kw in combined for kw in map_keywords)


def _auto_build_option(chart_type: str, df: "pd.DataFrame") -> dict:
    """Auto-build an ECharts option from chart_type using DataFrame columns.

    This is the safety net — when a caller passes only ``chart_type``
    without an explicit ``echarts_option``, we infer sensible defaults
    so the chart always renders.
    """
    cols = list(df.columns)
    if not cols:
        return {}

    # Map single-result queries to a gauge-like display
    if len(cols) == 1 and len(df) == 1:
        val = df.iloc[0, 0]
        return {"series": [{"type": "gauge", "data": [{"value": float(val) if val is not None else 0, "name": cols[0]}]}]}

    first_col = cols[0]
    second_col = cols[1] if len(cols) > 1 else first_col

    ct = chart_type.lower()

    if ct in ("bar", "column"):
        return {
            "xAxis": {"type": "category"},
            "yAxis": {"type": "value"},
            "series": [{"type": "bar", "encode": {"x": first_col, "y": second_col}}],
        }
    elif ct == "line":
        return {
            "xAxis": {"type": "category"},
            "yAxis": {"type": "value"},
            "series": [{"type": "line", "encode": {"x": first_col, "y": second_col}}],
        }
    elif ct == "pie":
        return {
            "series": [{"type": "pie", "encode": {"itemName": first_col, "value": second_col},
                        "radius": ["40%", "70%"]}],
        }
    elif ct == "scatter":
        return {
            "xAxis": {"type": "value"},
            "yAxis": {"type": "value"},
            "series": [{"type": "scatter", "encode": {"x": first_col, "y": second_col}}],
        }
    elif ct == "map":
        # Map charts MUST use data array (not dataset+encode) for reliable
        # rendering. visualMap is REQUIRED to show value-based coloring.
        map_name = "china"
        data = []
        values = []
        for _, row in df.iterrows():
            name_val = str(row[first_col]) if row[first_col] is not None else ""
            num_val = float(row[second_col]) if row[second_col] is not None else 0
            data.append({"name": name_val, "value": num_val})
            values.append(num_val)
        return {
            "visualMap": {
                "min": min(values) if values else 0,
                "max": max(values) if values else 100,
                "text": ["高", "低"],
                "realtime": False,
                "calculable": True,
                "inRange": {"color": ["#e0f3f8", "#abd9e9", "#74add1", "#4575b4", "#313695"]},
            },
            "series": [{"type": "map", "map": map_name, "data": data}],
        }
    elif ct == "radar":
        # Build radar indicators from remaining columns
        indicators = [{"name": c, "max": float(df[c].max()) * 1.2 if df[c].dtype in ('float64','int64') else 100}
                      for c in cols[1:]]
        return {
            "radar": {"indicator": indicators},
            "series": [{"type": "radar", "encode": {"itemName": first_col, "value": cols[1:]}}],
        }
    # Default: bar chart
    return {
        "xAxis": {"type": "category"},
        "yAxis": {"type": "value"},
        "series": [{"type": "bar", "encode": {"x": first_col, "y": second_col}}],
    }


# ---------------------------------------------------------------------------
# Chart-type minimum requirements — every type MUST satisfy these
# ---------------------------------------------------------------------------

CHART_REQUIREMENTS = {
    "bar": {
        "required_keys": ["xAxis", "yAxis", "series"],
        "series_type": "bar",
        "fixups": [
            ("xAxis", {"type": "category"}),
            ("yAxis", {"type": "value"}),
        ],
    },
    "line": {
        "required_keys": ["xAxis", "yAxis", "series"],
        "series_type": "line",
        "fixups": [
            ("xAxis", {"type": "category"}),
            ("yAxis", {"type": "value"}),
        ],
    },
    "pie": {
        "required_keys": ["series"],
        "series_type": "pie",
        "fixups": [],
    },
    "scatter": {
        "required_keys": ["xAxis", "yAxis", "series"],
        "series_type": "scatter",
        "fixups": [
            ("xAxis", {"type": "value"}),
            ("yAxis", {"type": "value"}),
        ],
    },
    "map": {
        "required_keys": ["series", "visualMap"],
        "series_type": "map",
        "fixups": [],
    },
    "radar": {
        "required_keys": ["radar", "series"],
        "series_type": "radar",
        "fixups": [],
    },
}


def _df_to_json_safe(df: "pd.DataFrame") -> None:
    """Convert non-JSON-serializable columns to string in-place.

    DuckDB returns Python date/datetime objects which json.dumps cannot handle.
    """
    from datetime import date, datetime
    import numpy as np
    for col in df.columns:
        # Check pandas datetime types
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)
            continue
        # Check object columns containing date/datetime
        sample = df[col].dropna()
        if len(sample) > 0 and isinstance(sample.iloc[0], (date, datetime)):
            df[col] = df[col].astype(str)


def _validate_and_fix_option(option: dict, chart_type: str, df_columns: list) -> dict:
    """Hard guarantee: option MUST have everything needed to render.

    This is the LAST line of defense before HTML generation. It:
    1. Checks the chart type's minimum required keys exist
    2. Ensures every series has a ``type``
    3. Applies type-specific fixups if anything is missing
    """
    ct = chart_type.lower() if chart_type else ""
    req = CHART_REQUIREMENTS.get(ct, CHART_REQUIREMENTS["bar"])
    repaired = dict(option)

    # 1. Ensure required top-level keys exist
    for key in req["required_keys"]:
        if key not in repaired:
            repaired[key] = {}

    # 2. Apply fixups for missing sub-structures
    for key, default_val in req["fixups"]:
        if key not in repaired or not repaired[key]:
            repaired[key] = default_val
            logger.warning(f"自动补齐: {ct} chart 缺少 {key}，已注入默认值")

    # 3. Ensure series exists and every series has a type
    series_list = repaired.get("series", [])
    if not series_list:
        cols = list(df_columns)
        if len(cols) >= 2:
            repaired["series"] = [{"type": req["series_type"],
                                    "encode": {"x": cols[0], "y": cols[1]}}]
        else:
            repaired["series"] = [{"type": req["series_type"], "data": []}]
        logger.warning(f"自动补齐: {ct} chart 缺少 series，已注入 type={req['series_type']}")
    else:
        for i, s in enumerate(series_list):
            if not s.get("type"):
                repaired["series"][i]["type"] = req["series_type"]
                logger.warning(f"自动补齐: series[{i}] 缺少 type，已设为 {req['series_type']}")

    # 4. Map-specific: visualMap must have min/max/inRange
    if ct == "map":
        vm = repaired.get("visualMap", {})
        if "min" not in vm or "max" not in vm:
            # Extract values from series data
            data_vals = []
            for s in repaired.get("series", []):
                for d in s.get("data", []):
                    if isinstance(d, dict) and "value" in d:
                        data_vals.append(d["value"])
            if data_vals:
                vm["min"] = min(data_vals)
                vm["max"] = max(data_vals)
            else:
                vm["min"] = 0
                vm["max"] = 100
            repaired["visualMap"] = vm
            logger.warning(f"自动补齐: map visualMap min/max 从数据推断")
        if "inRange" not in vm:
            vm["inRange"] = {"color": ["#e0f3f8", "#abd9e9", "#74add1", "#4575b4", "#313695"]}
            repaired["visualMap"] = vm
        if "calculable" not in vm:
            vm["calculable"] = True
            repaired["visualMap"] = vm

    return repaired


def generate_echarts_html(df, config, output_path):
    """Generate an interactive HTML file using ECharts configuration.

    The generated HTML is a **self-contained** single file with the ECharts
    library and all required map scripts embedded inline — no external
    script references, no dependency on a running local server.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    baidu_ak = get_baidu_ak()
    bmap_script = ""

    title = config.get("title", "Chart")
    custom_js = config.get("custom_js", "")
    option = config.get("echarts_option", {})
    chart_type = config.get("chart_type", "")

    # Convert any non-JSON-serializable columns BEFORE building option/dataset
    for col in df.columns:
        try:
            json.dumps(df[col].iloc[0] if len(df) > 0 else None)
        except (TypeError, ValueError):
            df[col] = df[col].astype(str)

    # 0. Auto-build option from chart_type when no explicit echarts_option
    if not option and chart_type:
        option = _auto_build_option(chart_type, df)

    # 1. Automatic Dataset — only for types that support it.
    #    Types needing direct data arrays get data injected into series.
    series_has_data = any(s.get("data") for s in option.get("series", []))
    if not df.empty:
        cols = list(df.columns)
        rows = df.values.tolist()
        dataset_source = [cols] + rows
        stype = option.get("series", [{}])[0].get("type", "")

        # Determine if this scatter uses geo coordinateSystem (needs data array)
        is_geo_scatter = (stype == "scatter" and
                          option.get("series", [{}])[0].get("coordinateSystem") == "geo")

        # Types that need series.data (NOT dataset):
        if stype in ("pie", "map", "radar", "funnel", "gauge", "treemap", "sunburst",
                      "sankey", "graph", "tree", "parallel", "themeRiver", "pictorialBar",
                      "chord", "lines", "effectScatter", "bar3D", "scatter3D", "surface", "line3D") \
           or is_geo_scatter:
            if not series_has_data and len(cols) >= 2:
                data = []
                multi_dim = stype in ("radar", "parallel")  # value = array of dimensions
                for row in rows:
                    if multi_dim and len(row) > 2:
                        v = [float(x) if x is not None else 0 for x in row[1:]]
                    elif is_geo_scatter and len(row) >= 4:
                        # Column order: name, val, lat, lng → data needs [lng, lat, val]
                        v = [row[3], row[2], row[1]] if len(row) >= 4 else row[1]
                    elif is_geo_scatter and len(row) == 3:
                        v = row[1]  # name, lat, lng → [lat, lng]? use as-is
                    else:
                        v = row[1] if row[1] is not None else 0
                    data.append({"name": str(row[0]), "value": v})
                option.setdefault("series", [{}])[0]["data"] = data
        else:
            # Types that support dataset+encode: bar, line, scatter(cartesian), candlestick, boxplot, heatmap
            if not option.get('dataset'):
                option['dataset'] = {'source': dataset_source}

    raw_data_json = json.dumps(df.to_dict(orient='records'), ensure_ascii=False, default=str)
    dataset_source_json = json.dumps(
        [df.columns.tolist()] + df.values.tolist(), ensure_ascii=False, default=str
    )
    custom_js = (
        f"var rawData = {raw_data_json};\n"
        f"var datasetSource = {dataset_source_json};\n"
        + custom_js
    )

    # 2. Map name normalization — normalise the DataFrame and option data
    #    so that "北京市" → "北京", "广东省" → "广东", etc.
    is_map = _is_map_chart(option, custom_js)
    if is_map:
        # Normalize the DataFrame if it has a 'name' column (common for map data)
        if 'name' in df.columns:
            name_col_idx = list(df.columns).index('name')
            df_values = df.values.tolist()
            for row_idx, row in enumerate(df_values):
                original_name = row[name_col_idx]
                normalized = normalize_map_name(str(original_name))
                if normalized != original_name:
                    df_values[row_idx][name_col_idx] = normalized
            # Rebuild DataFrame with normalized values
            import pandas as _pd
            df = _pd.DataFrame(df_values, columns=df.columns)

        # Rebuild dataset source from normalized DataFrame
        if not df.empty:
            dataset_source = [df.columns.tolist()] + df.values.tolist()
            option['dataset'] = {'source': dataset_source}

        # Normalize option series data
        for i, series in enumerate(option.get("series", [])):
            if "data" in series and isinstance(series["data"], list):
                option["series"][i]["data"] = normalize_map_data(
                    series["data"], name_key="name"
                )

    # Rebuild JSON strings from (possibly normalized) data
    raw_data_json = json.dumps(df.to_dict(orient='records'), ensure_ascii=False, default=str)
    dataset_source_json = json.dumps(
        [df.columns.tolist()] + df.values.tolist(), ensure_ascii=False, default=str
    )
    custom_js = (
        f"var rawData = {raw_data_json};\n"
        f"var datasetSource = {dataset_source_json};\n"
        + config.get("custom_js", "")
    )

    # 3. Load ECharts and map scripts via HTMLExporter for inline embedding
    exporter = HTMLExporter(base_dir)
    try:
        echarts_js = exporter._load_echarts()
    except FileNotFoundError:
        logger.error("ECharts 库文件缺失", path=exporter.assets_dir / exporter.ECHARTS_FILE)
        echarts_js = "/* ECharts library not found — chart rendering disabled */"

    # Detect 3D chart types — need echarts-gl
    gl_js = ""
    gl_types = {"bar3D", "scatter3D", "surface", "line3D", "lines3D", "scatterGL", "graphGL", "flowGL"}
    series_types = {s.get("type", "") for s in option.get("series", [])}
    if series_types & gl_types or option.get("globe"):
        gl_path = exporter.assets_dir / "echarts-gl.min.js"
        if gl_path.exists():
            with open(gl_path, "r", encoding="utf-8") as gf:
                gl_js = "<script>\n" + gf.read() + "\n</script>"
            logger.info("echarts-gl 已内联", gl_types=series_types & gl_types)

    # Ensure tooltip is enabled — off by default in some ECharts modes
    if "tooltip" not in option:
        option["tooltip"] = {}
    if "toolbox" not in option:
        option["toolbox"] = {"feature": {"saveAsImage": {}, "dataView": {"readOnly": False}}}

    # Fix scatter bubble: encode.z needs visualMap for symbol size variation
    for s in option.get("series", []):
        if s.get("type") == "scatter":
            # Geo scatter: compute per-point symbolSize in Python, apply as data item property
            if s.get("coordinateSystem") == "geo" and "symbolSize" not in s:
                sd = s.get("data", [])
                all_vals = []
                for d in sd:
                    v = d.get("value", 0)
                    if isinstance(v, list) and len(v) >= 3:
                        all_vals.append(v[2])
                    elif isinstance(v, (int, float)):
                        all_vals.append(v)
                if all_vals:
                    mn, mx = min(all_vals), max(all_vals)
                    rng = mx - mn if mx != mn else 1
                    for d in sd:
                        v = d.get("value", 0)
                        num = v[2] if isinstance(v, list) and len(v) >= 3 else (v if isinstance(v, (int, float)) else 1)
                        d["symbolSize"] = round(8 + (num - mn) / rng * 40, 1)
                    s.pop("symbolSize", None)  # remove series-level, use per-point
            # Convert string symbolSize → encode.z (dimension reference)
            if isinstance(s.get("symbolSize"), str) and "z" not in s.get("encode", {}):
                s.setdefault("encode", {})["z"] = s.pop("symbolSize")
            # Auto-add visualMap for varying symbol size (bubble charts only, not geo)
            enc = s.get("encode", {})
            is_geo = s.get("coordinateSystem") == "geo"
            need_vm = ("z" in enc) and not is_geo  # only for cartesian bubble scatter
            if need_vm and "visualMap" not in option:
                z_dim = enc.get("z") or enc.get("value", "")
                # Find the column index from dataset source
                src = option.get("dataset", {}).get("source", [])
                vals = []
                if len(src) > 1 and z_dim in src[0]:
                    ci = src[0].index(z_dim)
                    for row in src[1:]:
                        try: vals.append(float(row[ci]))
                        except: pass
                # Also check series.data for direct data format (geo scatter)
                if not vals and s.get("data"):
                    for d in s["data"]:
                        v = d.get("value", 0)
                        if isinstance(v, (int, float)): vals.append(v)
                        elif isinstance(v, list) and len(v) >= 3: vals.append(v[2])
                if vals:
                    option["visualMap"] = {
                        "dimension": 2,
                        "min": min(vals), "max": max(vals),
                        "inRange": {"symbolSize": [5, 60]},
                        "orient": "vertical", "right": 10
                    }

    # Hard guarantee: option MUST have a renderable series type
    option = _validate_and_fix_option(option, chart_type, df.columns)

    option_json = json.dumps(option, ensure_ascii=False)
    required_maps = exporter._detect_required_maps(option_json, custom_js)
    map_scripts_inline = "\n".join(
        exporter._load_map_script(m) for m in required_maps if exporter._load_map_script(m)
    )

    # 4. BMap script injection (requires remote Baidu Maps API)
    bmap_script = ""
    if ("bmap" in json.dumps(option) or "bmap" in custom_js) and baidu_ak:
        bmap_script = (
            f'<script type="text/javascript" '
            f'src="https://api.map.baidu.com/api?v=3.0&ak={baidu_ak}"></script>\n'
            '        <script>\n'
        )
        # Embed bmap.min.js inline if available
        bmap_js = exporter._load_map_script("bmap.min")
        if bmap_js:
            bmap_script += bmap_js
        bmap_script += '\n        </script>'

    # 5. Determine server / file-path output
    cfg = get_config()

    # Resolve output directory from config
    output_dir = cfg.output.dir if cfg.output.dir else "outputs/html"
    # If output_path is relative or bare filename, prepend output_dir
    if not os.path.isabs(output_path):
        output_path = os.path.join(base_dir, output_dir, os.path.basename(output_path))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    title_escaped = html_mod.escape(title)

    # Escape </script> sequences in JSON strings for safe script embedding
    option_safe = option_json.replace('</', '<\\/')
    data_safe = raw_data_json.replace('</', '<\\/')

    # Build self-contained HTML with embedded scripts
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title_escaped}</title>
</head>
<body>
    <div id="main" style="width: 100%; height: 800px;"></div>
    <script>
{echarts_js}
    </script>
{gl_js}
    <script>
{map_scripts_inline}
    </script>
    {bmap_script}
    <script type="text/javascript">
        (function() {{
            var myChart = echarts.init(document.getElementById('main'));
            var option = {option_safe};
            var rawData = {data_safe};

            {config.get("custom_js", "")}

            myChart.setOption(option);
            window.addEventListener('resize', function() {{
                myChart.resize();
            }});
        }})();
    </script>
</body>
</html>
"""

    with io.open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    abs_path = os.path.abspath(output_path)
    rel_path = os.path.relpath(output_path, base_dir).replace(os.sep, '/')

    # Build access info based on server config
    if cfg.server.enabled:
        base_url = ensure_server_running()
        if base_url is None:
            logger.warning("Server failed to start, showing file path as fallback")
            access_info = f"file://{abs_path}"
        else:
            access_info = f"{base_url}/{rel_path}"
    else:
        access_info = f"file://{abs_path}"

    logger.info(
        "ECharts 图表已生成",
        output_path=abs_path,
        access=access_info,
        server_enabled=cfg.server.enabled,
        rows=len(df),
        maps_embedded=len(required_maps),
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
        "db_path": "workspace.duckdb",
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
    db_path = config.get("db_path", "workspace.duckdb")
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
    # Use configured output directory as default
    try:
        cfg = get_config()
        output_dir = cfg.output.dir if cfg.output.dir else "outputs/html"
    except Exception:
        output_dir = "outputs/html"
    default_output = os.path.join(base_dir, output_dir, "chart.html")
    output_path = config.get("output_path", default_output)
    if not output_path.endswith('.html'):
        output_path = os.path.splitext(output_path)[0] + '.html'

    return generate_echarts_html(df, config, output_path)

if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(description="Universal Chart Generator from DuckDB")
    parser.add_argument("--config", required=True, help="JSON string or path to .txt file containing chart configuration")

    args = parser.parse_args()

    try:
        if os.path.isfile(args.config):
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = json.loads(args.config)

        result = generate_chart(config)
        if result:
            print(f"✅ 图表已生成: {result}")
    except Exception as e:
        logger.error("图表生成失败", error=str(e), config=config if 'config' in dir() else None)
