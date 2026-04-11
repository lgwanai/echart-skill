"""
HTML Exporter Module.

Exports charts, dashboards, and Gantt charts as standalone HTML files
with all scripts and data embedded for offline sharing.

Features:
- Inline ECharts library (~1.1MB)
- Conditionally embed map scripts (china.js, world.js, provinces)
- No external dependencies - works offline
- Configurable themes
- Data size logging for user awareness
"""

import json
import os
from pathlib import Path
from typing import Optional

import pandas as pd

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_config import get_logger

logger = get_logger(__name__)


class HTMLExporter:
    """Export visualizations as standalone HTML with embedded scripts.
    
    Features:
    - Inline ECharts library (~1.1MB)
    - Conditionally embed map scripts (china.js, world.js, provinces)
    - No external dependencies - works offline
    - Configurable themes
    
    Example:
        exporter = HTMLExporter()
        html = exporter.generate_standalone_html(
            title="My Chart",
            option_json='{"xAxis": {"type": "category"}, "series": [{"type": "bar"}]}',
            data_json='[{"category": "A", "value": 100}]'
        )
        exporter.export_to_file(html, "output.html")
    """
    
    ASSETS_DIR = "assets/echarts"
    ECHARTS_FILE = "echarts.min.js"
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialize exporter with assets directory.
        
        Args:
            base_dir: Project root directory. Auto-detected if not provided.
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.assets_dir = self.base_dir / self.ASSETS_DIR
        self._echarts_content: Optional[str] = None
        self._map_cache: dict[str, str] = {}
    
    def _load_echarts(self) -> str:
        """Load ECharts library content (cached).
        
        Returns:
            ECharts library JavaScript content as string.
            
        Raises:
            FileNotFoundError: If echarts.min.js not found in assets directory.
        """
        if self._echarts_content is None:
            echarts_path = self.assets_dir / self.ECHARTS_FILE
            if not echarts_path.exists():
                raise FileNotFoundError(f"ECharts library not found: {echarts_path}")
            with open(echarts_path, 'r', encoding='utf-8') as f:
                self._echarts_content = f.read()
            logger.info(
                "ECharts library loaded",
                size_kb=len(self._echarts_content) // 1024
            )
        return self._echarts_content
    
    def _load_map_script(self, map_name: str) -> str:
        """Load map script content (cached).
        
        Args:
            map_name: Map filename without extension (e.g., 'china', 'world', 'beijing')
            
        Returns:
            Map script JavaScript content, or empty string if not found.
        """
        if map_name not in self._map_cache:
            map_path = self.assets_dir / f"{map_name}.js"
            if map_path.exists():
                with open(map_path, 'r', encoding='utf-8') as f:
                    self._map_cache[map_name] = f.read()
                logger.debug("Map script loaded", map=map_name)
            else:
                self._map_cache[map_name] = ""
                logger.warning("Map script not found", map=map_name)
        return self._map_cache[map_name]
    
    def _detect_required_maps(self, option_json: str, custom_js: str) -> list[str]:
        """Detect which map scripts are needed based on chart config.
        
        Args:
            option_json: JSON string of echarts option
            custom_js: Custom JavaScript code
            
        Returns:
            List of map script filenames to embed
        """
        combined = option_json + custom_js
        maps = []
        
        # Province name to pinyin mapping
        province_map = {
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
        
        # Check for china map
        if "china" in combined or "中国" in combined:
            maps.append("china")
        
        # Check for world map
        if "world" in combined or "世界" in combined:
            maps.append("world")
        
        # Check for province maps
        for cn_name, pinyin in province_map.items():
            if cn_name in combined or pinyin in combined:
                maps.append(pinyin)
        
        return maps
    
    def generate_standalone_html(
        self,
        title: str,
        option_json: str,
        data_json: str,
        custom_js: str = "",
        theme: str = "default",
        full_screen: bool = True
    ) -> str:
        """Generate standalone HTML with all scripts embedded.
        
        Args:
            title: Chart title (displayed at top of page)
            option_json: JSON string of echarts option
            data_json: JSON string of chart data (for rawData access in custom_js)
            custom_js: Additional JavaScript code
            theme: ECharts theme name (default, dark, etc.)
            full_screen: If True, chart takes full viewport
            
        Returns:
            Complete HTML string with embedded scripts
            
        Example:
            html = exporter.generate_standalone_html(
                title="Sales Chart",
                option_json='{"xAxis": {"type": "category"}, "series": [{"type": "bar"}]}',
                data_json='[{"category": "Q1", "value": 100}]'
            )
        """
        # Load ECharts
        echarts_content = self._load_echarts()
        
        # Detect and load required maps
        required_maps = self._detect_required_maps(option_json, custom_js)
        map_scripts = "\n".join(
            self._load_map_script(m) for m in required_maps
        )
        
        # Build style based on full_screen flag
        if full_screen:
            style = """
        body { margin: 0; padding: 0; }
        #main { width: 100%; height: 100vh; }
        #title { 
            position: absolute; 
            top: 10px; 
            left: 0; 
            right: 0; 
            text-align: center; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 18px;
            font-weight: 500;
            z-index: 100;
        }
            """
        else:
            style = """
        body { margin: 20px; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        #main { width: 100%; height: 600px; }
        #title { font-size: 18px; font-weight: 500; margin-bottom: 10px; }
            """
        
        # Theme initialization
        theme_js = ""
        if theme == "dark":
            theme_js = "myChart.setOption({ backgroundColor: '#1a1a1a' });"
        
        # Build HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>{style}
    </style>
</head>
<body>
    <div id="title">{title}</div>
    <div id="main"></div>
    <script>
{echarts_content}
    </script>
    <script>
{map_scripts}
    </script>
    <script type="text/javascript">
        (function() {{
            var myChart = echarts.init(document.getElementById('main'));
            var option = {option_json};
            var rawData = {data_json};
            {custom_js}
            myChart.setOption(option);
            {theme_js}
            window.addEventListener('resize', function() {{
                myChart.resize();
            }});
        }})();
    </script>
</body>
</html>"""
        
        # Log embedded size
        total_size = len(html)
        data_size = len(data_json)
        logger.info(
            "Standalone HTML generated",
            title=title,
            total_size_kb=total_size // 1024,
            data_size_kb=data_size // 1024,
            maps_embedded=len(required_maps)
        )
        
        return html
    
    def export_to_file(self, html: str, output_path: str) -> str:
        """Write HTML to file.
        
        Args:
            html: HTML content
            output_path: Output file path
            
        Returns:
            Absolute path to output file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info("HTML exported", path=str(output_path.absolute()))
        return str(output_path.absolute())


if __name__ == "__main__":  # pragma: no cover
    import argparse
    
    parser = argparse.ArgumentParser(description="HTML Exporter - Standalone HTML Generation")
    parser.add_argument("--test", action="store_true", help="Run self-test")
    
    args = parser.parse_args()
    
    if args.test:
        # Self-test: generate a simple chart
        exporter = HTMLExporter()
        test_option = '{"xAxis": {"type": "category", "data": ["A", "B", "C"]}, "yAxis": {"type": "value"}, "series": [{"type": "bar", "data": [10, 20, 30]}]}'
        test_data = '[{"category": "A", "value": 10}, {"category": "B", "value": 20}, {"category": "C", "value": 30}]'
        html = exporter.generate_standalone_html("Test Chart", test_option, test_data)
        print(f"Generated HTML: {len(html)} bytes")
        print(f"ECharts embedded: {len(exporter._echarts_content or '')} bytes")
