import pytest
import os
import sys
import sqlite3
import json

# Mock the server module before importing chart_generator
import unittest.mock as mock
sys.modules['server'] = mock.MagicMock()
sys.modules['server'].ensure_server_running = mock.MagicMock(return_value='http://localhost:8080')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.chart_generator import (
    generate_chart,
    generate_echarts_html,
    replace_placeholders,
    get_baidu_ak,
    get_geo_coord,
)


class TestReplacePlaceholders:
    """Test placeholder replacement."""

    def test_simple_replacement(self):
        """Simple placeholders should be replaced."""
        obj = {"title": "{title}", "value": "{value}"}
        result = replace_placeholders(obj, {"title": "My Chart", "value": 100})
        assert result["title"] == "My Chart"
        assert result["value"] == 100

    def test_nested_replacement(self):
        """Nested placeholders should be replaced."""
        obj = {
            "title": "{title}",
            "series": [{"name": "{series_name}"}]
        }
        result = replace_placeholders(obj, {"title": "Test", "series_name": "Data"})
        assert result["series"][0]["name"] == "Data"

    def test_partial_replacement(self):
        """Partial string replacement should work."""
        obj = {"title": "Chart for {metric}"}
        result = replace_placeholders(obj, {"metric": "Sales"})
        assert result["title"] == "Chart for Sales"

    def test_no_replacement(self):
        """Objects without placeholders should be unchanged."""
        obj = {"title": "Static Title", "value": 123}
        result = replace_placeholders(obj, {"unused": "value"})
        assert result["title"] == "Static Title"
        assert result["value"] == 123

    def test_numeric_value_replacement(self):
        """Numeric values should be converted to string in partial replacement."""
        obj = {"label": "Total: {count}"}
        result = replace_placeholders(obj, {"count": 42})
        assert result["label"] == "Total: 42"

    def test_list_replacement(self):
        """Placeholders in lists should be replaced."""
        obj = ["{item1}", "{item2}", "static"]
        result = replace_placeholders(obj, {"item1": "first", "item2": "second"})
        assert result[0] == "first"
        assert result[1] == "second"
        assert result[2] == "static"

    def test_deeply_nested_replacement(self):
        """Deeply nested placeholders should be replaced."""
        obj = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "{deep_value}"
                    }
                }
            }
        }
        result = replace_placeholders(obj, {"deep_value": "found"})
        assert result["level1"]["level2"]["level3"]["value"] == "found"


class TestGenerateEchartsHTML:
    """Test HTML generation."""

    def test_html_structure(self, temp_output_dir):
        """Generated HTML should have proper structure."""
        import pandas as pd

        df = pd.DataFrame({"name": ["A", "B"], "value": [10, 20]})
        config = {
            "title": "Test Chart",
            "echarts_option": {
                "xAxis": {"type": "category"},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar"}]
            }
        }
        output_path = os.path.join(temp_output_dir, "test.html")

        import unittest.mock as mock
        with mock.patch('scripts.chart_generator.get_baidu_ak', return_value=None):
            result = generate_echarts_html(df, config, output_path)

        assert os.path.exists(output_path)
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "<!DOCTYPE html>" in content
        assert "echarts.min.js" in content
        assert "Test Chart" in content

    def test_html_with_dataset(self, temp_output_dir):
        """HTML should include dataset when no custom dataset."""
        import pandas as pd

        df = pd.DataFrame({"category": ["A", "B"], "value": [10, 20]})
        config = {
            "title": "Dataset Test",
            "echarts_option": {
                "series": [{"type": "bar"}]
            }
        }
        output_path = os.path.join(temp_output_dir, "dataset.html")

        import unittest.mock as mock
        with mock.patch('scripts.chart_generator.get_baidu_ak', return_value=None):
            generate_echarts_html(df, config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Should have dataset in the option
        assert "dataset" in content.lower()

    def test_html_with_custom_js(self, temp_output_dir):
        """HTML should include custom JS code."""
        import pandas as pd

        df = pd.DataFrame({"name": ["A"], "value": [10]})
        config = {
            "title": "Custom JS Test",
            "custom_js": "console.log('custom code');",
            "echarts_option": {"series": [{"type": "bar"}]}
        }
        output_path = os.path.join(temp_output_dir, "custom.html")

        import unittest.mock as mock
        with mock.patch('scripts.chart_generator.get_baidu_ak', return_value=None):
            generate_echarts_html(df, config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "custom code" in content
        assert "rawData" in content  # Raw data should be exposed to custom JS

    def test_html_preserves_chinese(self, temp_output_dir):
        """HTML should preserve Chinese characters."""
        import pandas as pd

        df = pd.DataFrame({"category": ["北京", "上海"], "value": [100, 200]})
        config = {
            "title": "中文测试图表",
            "echarts_option": {"series": [{"type": "bar"}]}
        }
        output_path = os.path.join(temp_output_dir, "chinese.html")

        import unittest.mock as mock
        with mock.patch('scripts.chart_generator.get_baidu_ak', return_value=None):
            generate_echarts_html(df, config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "中文测试图表" in content
        assert "北京" in content
        assert "上海" in content


class TestGenerateChart:
    """Test chart generation from config."""

    @pytest.fixture
    def populated_db(self, temp_db):
        """Create a database with test data."""
        conn = sqlite3.connect(temp_db)
        conn.execute('''
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY,
                category TEXT,
                amount REAL
            )
        ''')
        conn.execute("INSERT INTO sales (category, amount) VALUES ('A', 100)")
        conn.execute("INSERT INTO sales (category, amount) VALUES ('B', 200)")
        conn.commit()
        conn.close()
        return temp_db

    def test_generate_chart_from_query(self, populated_db, temp_output_dir):
        """Chart should be generated from SQL query."""
        config = {
            "db_path": populated_db,
            "query": "SELECT category, amount FROM sales",
            "title": "Sales Chart",
            "output_path": os.path.join(temp_output_dir, "sales.html"),
            "echarts_option": {
                "xAxis": {"type": "category"},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar"}]
            }
        }

        import unittest.mock as mock
        with mock.patch('scripts.chart_generator.get_baidu_ak', return_value=None):
            result = generate_chart(config)

        assert result is not None
        assert os.path.exists(result)

    def test_generate_chart_empty_result(self, populated_db, temp_output_dir):
        """Empty query result should be handled gracefully."""
        config = {
            "db_path": populated_db,
            "query": "SELECT category, amount FROM sales WHERE 1=0",
            "title": "Empty Chart",
            "output_path": os.path.join(temp_output_dir, "empty.html"),
        }

        result = generate_chart(config)

        # Should return None for empty data
        assert result is None

    def test_generate_chart_missing_query(self, temp_output_dir):
        """Missing query should raise error."""
        config = {
            "db_path": "test.db",
            "title": "No Query",
            "output_path": os.path.join(temp_output_dir, "no_query.html"),
        }

        with pytest.raises(ValueError, match="Missing SQL query"):
            generate_chart(config)

    def test_generate_chart_missing_db(self, temp_output_dir):
        """Missing database should be handled."""
        config = {
            "db_path": "/nonexistent/path.db",
            "query": "SELECT 1",
            "title": "Missing DB",
            "output_path": os.path.join(temp_output_dir, "missing_db.html"),
        }

        with pytest.raises(Exception):  # sqlite3.OperationalError
            generate_chart(config)

    def test_generate_chart_default_output_path(self, populated_db):
        """Chart should use default output path if not specified."""
        config = {
            "db_path": populated_db,
            "query": "SELECT category, amount FROM sales",
            "title": "Default Path Chart",
            "echarts_option": {"series": [{"type": "bar"}]}
        }

        import unittest.mock as mock
        with mock.patch('scripts.chart_generator.get_baidu_ak', return_value=None):
            result = generate_chart(config)

        # Should generate a path in outputs/html/
        assert result is not None
        assert "outputs" in result
        assert result.endswith(".html")

        # Cleanup
        if os.path.exists(result):
            os.unlink(result)

    def test_generate_chart_non_html_extension(self, populated_db, temp_output_dir):
        """Non-HTML extension should be converted to .html."""
        config = {
            "db_path": populated_db,
            "query": "SELECT category, amount FROM sales",
            "title": "Extension Test",
            "output_path": os.path.join(temp_output_dir, "chart.txt"),
            "echarts_option": {"series": [{"type": "bar"}]}
        }

        import unittest.mock as mock
        with mock.patch('scripts.chart_generator.get_baidu_ak', return_value=None):
            result = generate_chart(config)

        assert result.endswith(".html")


class TestGetBaiduAK:
    """Test Baidu AK retrieval."""

    def test_get_baidu_ak_from_env(self, monkeypatch):
        """Should get AK from environment variable."""
        monkeypatch.setenv('BAIDU_AK', 'test_ak_from_env')
        result = get_baidu_ak()
        assert result == 'test_ak_from_env'

    def test_get_baidu_ak_missing(self, monkeypatch):
        """Should return None when no AK available."""
        monkeypatch.delenv('BAIDU_AK', raising=False)
        with mock.patch('scripts.chart_generator.os.path.exists', return_value=False):
            result = get_baidu_ak()
            assert result is None


class TestGetGeoCoord:
    """Test geocoding functionality."""

    def test_get_geo_coord_from_cache(self, tmp_path, monkeypatch):
        """Should return cached coordinates."""
        import json

        # Setup cache file with existing data
        references_dir = tmp_path / "references"
        references_dir.mkdir(parents=True, exist_ok=True)
        cache_file = references_dir / "geo_cache.json"
        cache_data = {"Beijing": [116.4074, 39.9042]}
        cache_file.write_text(json.dumps(cache_data))

        # Patch the base_dir calculation in get_geo_coord
        with mock.patch('scripts.chart_generator.os.path.dirname', return_value=str(tmp_path)):
            with mock.patch('scripts.chart_generator.os.path.exists', return_value=True):
                with mock.patch('scripts.chart_generator.os.makedirs'):
                    result = get_geo_coord("Beijing", "any_ak")

        assert result == [116.4074, 39.9042]


class TestHTMLWithMapScripts:
    """Test HTML generation with map scripts."""

    def test_html_with_china_map(self, temp_output_dir):
        """HTML should include china.js when china map is used."""
        import pandas as pd

        df = pd.DataFrame({"name": ["Beijing"], "value": [100]})
        config = {
            "title": "China Map",
            "echarts_option": {
                "geo": {"map": "china"}
            }
        }
        output_path = os.path.join(temp_output_dir, "china.html")

        with mock.patch('scripts.chart_generator.get_baidu_ak', return_value=None):
            generate_echarts_html(df, config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "china.js" in content

    def test_html_with_world_map(self, temp_output_dir):
        """HTML should include world.js when world map is used."""
        import pandas as pd

        df = pd.DataFrame({"name": ["USA"], "value": [100]})
        config = {
            "title": "World Map",
            "echarts_option": {
                "geo": {"map": "world"}
            }
        }
        output_path = os.path.join(temp_output_dir, "world.html")

        with mock.patch('scripts.chart_generator.get_baidu_ak', return_value=None):
            generate_echarts_html(df, config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "world.js" in content

    def test_html_with_bmap(self, temp_output_dir):
        """HTML should include bmap script when bmap is used."""
        import pandas as pd

        df = pd.DataFrame({"name": ["Beijing"], "value": [100]})
        config = {
            "title": "BMap Chart",
            "echarts_option": {
                "bmap": {"center": [116.4074, 39.9042]}
            }
        }
        output_path = os.path.join(temp_output_dir, "bmap.html")

        with mock.patch('scripts.chart_generator.get_baidu_ak', return_value='test_ak'):
            generate_echarts_html(df, config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "bmap.min.js" in content
