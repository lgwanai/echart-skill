"""Integration tests for standalone HTML export functionality."""

import json
import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from database import get_repository
from scripts.chart_generator import export_standalone_chart
from scripts.dashboard_generator import export_standalone_dashboard


class TestChartExport:
    """Integration tests for chart export."""
    
    @pytest.fixture
    def sample_db(self, tmp_path):
        """Create sample database with test data."""
        db_path = tmp_path / "test.duckdb"
        repo = get_repository(str(db_path))
        
        df = pd.DataFrame({
            "category": ["A", "B", "C"],
            "value": [100, 200, 150]
        })
        
        with repo.connection() as conn:
            conn.execute("DROP TABLE IF EXISTS test_data")
            conn.execute("CREATE TABLE test_data AS SELECT * FROM df")
        
        return str(db_path)
    
    def test_export_chart_creates_html(self, sample_db, tmp_path):
        """Test that export creates valid HTML file."""
        output_path = tmp_path / "chart.html"
        
        config = {
            "db_path": sample_db,
            "query": "SELECT * FROM test_data",
            "title": "Test Chart",
            "echarts_option": {
                "xAxis": {"type": "category"},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar"}]
            }
        }
        
        result = export_standalone_chart(config, str(output_path))
        
        assert output_path.exists()
        assert result == str(output_path.absolute())
    
    def test_export_chart_contains_echarts(self, sample_db, tmp_path):
        """Test that exported HTML contains ECharts library."""
        output_path = tmp_path / "chart.html"
        
        config = {
            "db_path": sample_db,
            "query": "SELECT * FROM test_data",
            "title": "Test",
            "echarts_option": {"series": [{"type": "bar"}]}
        }
        
        export_standalone_chart(config, str(output_path))
        
        html = output_path.read_text(encoding='utf-8')
        
        assert "echarts" in html.lower()
        assert "echarts.init" in html
    
    def test_export_chart_contains_data(self, sample_db, tmp_path):
        """Test that exported HTML contains embedded data."""
        output_path = tmp_path / "chart.html"
        
        config = {
            "db_path": sample_db,
            "query": "SELECT * FROM test_data",
            "title": "Test",
            "echarts_option": {"series": [{"type": "bar"}]}
        }
        
        export_standalone_chart(config, str(output_path))
        
        html = output_path.read_text(encoding='utf-8')
        
        assert "rawData" in html
        assert '"category"' in html
        assert '"value"' in html
    
    def test_export_chart_chinese_characters(self, sample_db, tmp_path):
        """Test Chinese characters are preserved."""
        output_path = tmp_path / "chart.html"
        
        repo = get_repository(sample_db)
        df = pd.DataFrame({
            "城市": ["北京", "上海", "广州"],
            "数值": [100, 200, 150]
        })
        
        with repo.connection() as conn:
            conn.execute("DROP TABLE IF EXISTS chinese_data")
            conn.execute("CREATE TABLE chinese_data AS SELECT * FROM df")
        
        config = {
            "db_path": sample_db,
            "query": "SELECT * FROM chinese_data",
            "title": "中文图表",
            "echarts_option": {"series": [{"type": "bar"}]}
        }
        
        export_standalone_chart(config, str(output_path))
        
        html = output_path.read_text(encoding='utf-8')
        
        assert "中文图表" in html
        assert "北京" in html
        assert "上海" in html
    
    def test_export_chart_with_theme(self, sample_db, tmp_path):
        """Test chart export with dark theme."""
        output_path = tmp_path / "chart.html"
        
        config = {
            "db_path": sample_db,
            "query": "SELECT * FROM test_data",
            "title": "Dark Theme",
            "echarts_option": {"series": [{"type": "bar"}]}
        }
        
        export_standalone_chart(config, str(output_path), theme="dark")
        
        html = output_path.read_text(encoding='utf-8')
        
        assert "#1a1a1a" in html


class TestDashboardExport:
    """Integration tests for dashboard export."""
    
    @pytest.fixture
    def sample_db(self, tmp_path):
        """Create sample database."""
        db_path = tmp_path / "test.duckdb"
        repo = get_repository(str(db_path))
        
        df = pd.DataFrame({
            "month": ["Jan", "Feb", "Mar"],
            "sales": [100, 200, 150],
            "costs": [50, 80, 60]
        })
        
        with repo.connection() as conn:
            conn.execute("DROP TABLE IF EXISTS dashboard_data")
            conn.execute("CREATE TABLE dashboard_data AS SELECT * FROM df")
        
        return str(db_path)
    
    @pytest.fixture
    def dashboard_config(self, sample_db, tmp_path):
        """Create dashboard configuration file."""
        config_path = tmp_path / "dashboard.json"
        
        config = {
            "title": "Test Dashboard",
            "columns": 2,
            "row_height": 400,
            "gap": 16,
            "db_path": sample_db,
            "charts": [
                {
                    "id": "chart1",
                    "position": {"row": 0, "col": 0, "row_span": 1, "col_span": 1},
                    "title": "Sales",
                    "query": "SELECT month, sales FROM dashboard_data",
                    "echarts_option": {
                        "xAxis": {"type": "category"},
                        "yAxis": {"type": "value"},
                        "series": [{"type": "bar"}]
                    }
                },
                {
                    "id": "chart2",
                    "position": {"row": 0, "col": 1, "row_span": 1, "col_span": 1},
                    "title": "Costs",
                    "query": "SELECT month, costs FROM dashboard_data",
                    "echarts_option": {
                        "xAxis": {"type": "category"},
                        "yAxis": {"type": "value"},
                        "series": [{"type": "line"}]
                    }
                }
            ]
        }
        
        config_path.write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
        return str(config_path)
    
    def test_export_dashboard_creates_html(self, dashboard_config, tmp_path):
        """Test that dashboard export creates valid HTML."""
        output_path = tmp_path / "dashboard.html"
        
        result = export_standalone_dashboard(dashboard_config, str(output_path))
        
        assert output_path.exists()
        assert result == str(output_path.absolute())
    
    def test_export_dashboard_contains_all_charts(self, dashboard_config, tmp_path):
        """Test that dashboard contains all chart containers."""
        output_path = tmp_path / "dashboard.html"
        
        export_standalone_dashboard(dashboard_config, str(output_path))
        
        html = output_path.read_text(encoding='utf-8')
        
        assert 'id="chart_chart1"' in html
        assert 'id="chart_chart2"' in html
    
    def test_export_dashboard_contains_echarts(self, dashboard_config, tmp_path):
        """Test that dashboard contains ECharts library."""
        output_path = tmp_path / "dashboard.html"
        
        export_standalone_dashboard(dashboard_config, str(output_path))
        
        html = output_path.read_text(encoding='utf-8')
        
        assert "echarts" in html.lower()
        assert "echarts.init" in html
    
    def test_export_dashboard_grid_layout(self, dashboard_config, tmp_path):
        """Test that dashboard has CSS Grid layout."""
        output_path = tmp_path / "dashboard.html"
        
        export_standalone_dashboard(dashboard_config, str(output_path))
        
        html = output_path.read_text(encoding='utf-8')
        
        assert "display: grid" in html
        assert "grid-template-columns" in html
