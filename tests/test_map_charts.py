"""
Test suite for map chart generation validation.
Validates all map chart templates and ensures they work correctly with local static maps.
"""

import pytest
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.chart_generator import generate_chart


class TestMapChartTemplates:
    """Test all map chart template scenarios."""

    @pytest.fixture
    def test_db(self, tmp_path):
        """Create a test DuckDB database with sample data."""
        import duckdb
        
        db_path = tmp_path / "test.duckdb"
        conn = duckdb.connect(str(db_path))
        
        # Create sample data for China map
        conn.execute("""
            CREATE TABLE china_sales AS
            SELECT 
                province,
                sales_amount,
                sales_count
            FROM (
                VALUES
                    ('北京', 15000, 200),
                    ('上海', 12000, 180),
                    ('广东', 18000, 250),
                    ('浙江', 10000, 150),
                    ('江苏', 11000, 170),
                    ('山东', 9000, 130),
                    ('河南', 8000, 120),
                    ('四川', 7000, 100),
                    ('湖北', 6000, 90),
                    ('湖南', 5000, 80)
            ) AS t(province, sales_amount, sales_count)
        """)
        
        # Create sample data for world map
        conn.execute("""
            CREATE TABLE world_sales AS
            SELECT 
                country,
                revenue,
                customers
            FROM (
                VALUES
                    ('China', 100000, 5000),
                    ('United States', 80000, 4000),
                    ('Japan', 60000, 3000),
                    ('Germany', 50000, 2500),
                    ('United Kingdom', 40000, 2000),
                    ('France', 35000, 1750),
                    ('India', 30000, 1500),
                    ('Russia', 25000, 1250),
                    ('Brazil', 20000, 1000),
                    ('Australia', 15000, 750)
            ) AS t(country, revenue, customers)
        """)
        
        # Create sample data for province map (Guangdong)
        conn.execute("""
            CREATE TABLE gd_cities AS
            SELECT 
                city,
                population,
                gdp
            FROM (
                VALUES
                    ('广州', 15000000, 28000),
                    ('深圳', 13000000, 32000),
                    ('东莞', 8000000, 9000),
                    ('佛山', 7000000, 11000),
                    ('中山', 3000000, 4000),
                    ('珠海', 2000000, 3500),
                    ('惠州', 4000000, 5000),
                    ('江门', 4000000, 3000)
            ) AS t(city, population, gdp)
        """)
        
        conn.close()
        return str(db_path)

    def test_china_static_map(self, test_db, tmp_path):
        """Test China map using local static china.js (NOT dynamic GeoJSON)."""
        config = {
            "db_path": test_db,
            "query": "SELECT province, sales_amount FROM china_sales",
            "title": "中国各省销售额分布",
            "output_path": str(tmp_path / "china_map.html"),
            "echarts_option": {
                "title": {
                    "text": "中国各省销售额分布",
                    "left": "center"
                },
                "tooltip": {
                    "trigger": "item",
                    "formatter": "{b}<br/>销售额: {c}万元"
                },
                "visualMap": {
                    "min": 5000,
                    "max": 18000,
                    "left": "left",
                    "top": "bottom",
                    "text": ["高", "低"],
                    "calculable": True,
                    "inRange": {
                        "color": ["#f7fbff", "#08306b"]
                    }
                },
                "series": [{
                    "name": "销售额",
                    "type": "map",
                    "map": "china",
                    "roam": True,
                    "label": {
                        "show": True
                    },
                    "data": []
                }]
            },
            "custom_js": ""
        }
        
        output = generate_chart(config)
        
        # Read generated HTML
        with open(output, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Validate local static map script is included
        assert "china.js" in html, "china.js script must be included for China map"
        assert "echarts.min.js" in html, "echarts.min.js must be included"
        
        # Validate NO remote CDN links
        assert "https://cdn.jsdelivr.net/npm/echarts" not in html, "Should NOT use remote CDN"
        assert "$.get" not in html, "Should NOT use dynamic $.get for GeoJSON loading"
        assert "registerMap" not in config["custom_js"], "Should NOT manually register map for china.js"
        
        # Validate map type (basic check)
        assert '"type": "map"' in html or "type: 'map'" in html or 'type: "map"' in html
        assert '"map": "china"' in html or "map: 'china'" in html or 'map: "china"' in html
        
        print(f"✅ China static map test passed: {output}")

    def test_world_static_map(self, test_db, tmp_path):
        """Test World map using local static world.js (NOT dynamic GeoJSON)."""
        config = {
            "db_path": test_db,
            "query": "SELECT country, revenue FROM world_sales",
            "title": "全球各国营收分布",
            "output_path": str(tmp_path / "world_map.html"),
            "echarts_option": {
                "title": {
                    "text": "全球各国营收分布",
                    "left": "center"
                },
                "tooltip": {
                    "trigger": "item",
                    "formatter": "{b}<br/>营收: {c}万美元"
                },
                "visualMap": {
                    "min": 15000,
                    "max": 100000,
                    "left": "left",
                    "top": "bottom",
                    "text": ["高", "低"],
                    "calculable": True,
                    "inRange": {
                        "color": ["#ffffbf", "#8c510a"]
                    }
                },
                "series": [{
                    "name": "营收",
                    "type": "map",
                    "map": "world",
                    "roam": True,
                    "label": {
                        "show": False
                    },
                    "data": []
                }]
            },
            "custom_js": ""
        }
        
        output = generate_chart(config)
        
        with open(output, 'r', encoding='utf-8') as f:
            html = f.read()
        
        assert "world.js" in html, "world.js script must be included for World map"
        assert "echarts.min.js" in html
        assert "https://cdn.jsdelivr.net/npm/echarts" not in html
        assert "$.get" not in html

    def test_bmap_mode_with_baidu_ak(self, test_db, tmp_path):
        """Test Baidu Map (bmap) mode when local static map is not sufficient."""
        config = {
            "db_path": test_db,
            "query": "SELECT province, sales_amount FROM china_sales",
            "title": "百度地图模式测试",
            "output_path": str(tmp_path / "bmap_test.html"),
            "echarts_option": {
                "bmap": {
                    "center": [104.114129, 35.550339],
                    "zoom": 5,
                    "roam": True,
                    "mapStyle": {
                        "styleJson": [{
                            "featureType": "water",
                            "elementType": "all",
                            "stylers": {"color": "#d1d1d1"}
                        }]
                    }
                },
                "series": [{
                    "name": "销售",
                    "type": "scatter",
                    "coordinateSystem": "bmap",
                    "data": []
                }]
            },
            "custom_js": "",
            "baidu_ak": "test_ak_placeholder"
        }
        
        output = generate_chart(config)
        
        with open(output, 'r', encoding='utf-8') as f:
            html = f.read()
        
        assert "bmap.min.js" in html, "bmap.min.js must be included for bmap mode"
        assert "api.map.baidu.com/api" in html, "Baidu Map API must be included"
        assert '"coordinateSystem": "bmap"' in html or 'coordinateSystem: "bmap"' in html


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])