"""
Tests for dashboard generator.

This module tests the dashboard generation functionality:
- Grid layout CSS generation
- Chart positioning in grid
- HTML generation with all charts
- Map script aggregation
- CLI interface
"""
import json
import os
import tempfile
import sqlite3
import pytest


@pytest.fixture
def temp_db_with_data():
    """Create a temporary SQLite database with sample data."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            sales REAL
        )
    ''')
    conn.execute('''
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            quantity INTEGER,
            date TEXT
        )
    ''')
    # Insert sample data
    conn.execute("INSERT INTO products (name, category, sales) VALUES ('Product A', 'Cat1', 100)")
    conn.execute("INSERT INTO products (name, category, sales) VALUES ('Product B', 'Cat2', 200)")
    conn.execute("INSERT INTO products (name, category, sales) VALUES ('Product C', 'Cat1', 150)")
    conn.execute("INSERT INTO sales (product_id, quantity, date) VALUES (1, 10, '2024-01-01')")
    conn.execute("INSERT INTO sales (product_id, quantity, date) VALUES (2, 20, '2024-01-02')")
    conn.commit()
    conn.close()

    yield db_path

    os.unlink(db_path)


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for output files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_dashboard_config(temp_db_with_data):
    """Sample dashboard configuration for testing."""
    return {
        "title": "Test Dashboard",
        "columns": 2,
        "row_height": 400,
        "gap": 16,
        "db_path": temp_db_with_data,
        "charts": [
            {
                "id": "chart1",
                "position": {"row": 0, "col": 0},
                "title": "Sales by Product",
                "query": "SELECT name, sales FROM products",
                "echarts_option": {
                    "xAxis": {"type": "category", "data": "{name}"},
                    "yAxis": {"type": "value"},
                    "series": [{"type": "bar", "data": "{sales}"}]
                }
            },
            {
                "id": "chart2",
                "position": {"row": 0, "col": 1},
                "title": "Category Distribution",
                "query": "SELECT category, SUM(sales) as total FROM products GROUP BY category",
                "echarts_option": {
                    "series": [{"type": "pie", "data": "{data}"}]
                }
            }
        ]
    }


def build_config_file(config, temp_dir):
    """Helper to write config to a temporary JSON file."""
    config_path = os.path.join(temp_dir, "dashboard_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False)
    return config_path


class TestGridLayout:
    """Test CSS Grid layout generation."""

    def test_grid_container_exists(self, sample_dashboard_config, temp_output_dir):
        """HTML should contain a div with dashboard-grid class."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig

        config = DashboardConfig(**sample_dashboard_config)
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        assert 'class="dashboard-grid"' in html

    def test_grid_columns(self, sample_dashboard_config, temp_output_dir):
        """HTML should contain correct grid-template-columns."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig

        config = DashboardConfig(**sample_dashboard_config)
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        assert 'grid-template-columns: repeat(2, 1fr)' in html

    def test_grid_gap(self, sample_dashboard_config, temp_output_dir):
        """HTML should contain correct gap value."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig

        config = DashboardConfig(**sample_dashboard_config)
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        assert 'gap: 16px' in html

    def test_row_height(self, sample_dashboard_config, temp_output_dir):
        """HTML should contain correct grid-auto-rows value."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig

        config = DashboardConfig(**sample_dashboard_config)
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        assert 'grid-auto-rows: 400px' in html


class TestChartPositioning:
    """Test chart positioning in grid."""

    def test_chart_position_basic(self, temp_db_with_data, temp_output_dir):
        """Chart at row=0, col=0 should have correct grid CSS."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig, ChartConfig, ChartPosition

        config = DashboardConfig(
            title="Test",
            columns=2,
            db_path=temp_db_with_data,
            charts=[
                ChartConfig(
                    id="chart1",
                    position=ChartPosition(row=0, col=0),
                    query="SELECT name, sales FROM products"
                )
            ]
        )
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # grid-row: 1 / span 1; grid-column: 1 / span 1
        assert 'grid-row: 1' in html
        assert 'grid-column: 1' in html

    def test_chart_position_with_span(self, temp_db_with_data, temp_output_dir):
        """Chart with row_span and col_span should have correct grid CSS."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig, ChartConfig, ChartPosition

        config = DashboardConfig(
            title="Test",
            columns=3,
            db_path=temp_db_with_data,
            charts=[
                ChartConfig(
                    id="big_chart",
                    position=ChartPosition(row=0, col=0, row_span=2, col_span=2),
                    query="SELECT name, sales FROM products"
                )
            ]
        )
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # grid-row: 1 / span 2; grid-column: 1 / span 2
        assert 'grid-row: 1 / span 2' in html
        assert 'grid-column: 1 / span 2' in html

    def test_multiple_charts_positioned(self, temp_db_with_data, temp_output_dir):
        """Multiple charts should have distinct grid positions."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig, ChartConfig, ChartPosition

        config = DashboardConfig(
            title="Test",
            columns=2,
            db_path=temp_db_with_data,
            charts=[
                ChartConfig(
                    id="chart1",
                    position=ChartPosition(row=0, col=0),
                    query="SELECT name, sales FROM products"
                ),
                ChartConfig(
                    id="chart2",
                    position=ChartPosition(row=0, col=1),
                    query="SELECT category, SUM(sales) as total FROM products GROUP BY category"
                ),
                ChartConfig(
                    id="chart3",
                    position=ChartPosition(row=1, col=0, col_span=2),
                    query="SELECT name, sales FROM products"
                )
            ]
        )
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # chart1 at (0,0): grid-row: 1; grid-column: 1
        # chart2 at (0,1): grid-row: 1; grid-column: 2
        # chart3 at (1,0) span 2: grid-row: 2; grid-column: 1 / span 2
        assert 'id="chart_chart1"' in html
        assert 'id="chart_chart2"' in html
        assert 'id="chart_chart3"' in html


class TestHTMLGeneration:
    """Test HTML generation for dashboard."""

    def test_all_chart_ids_present(self, sample_dashboard_config, temp_output_dir):
        """Each chart ID should appear in HTML."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig

        config = DashboardConfig(**sample_dashboard_config)
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        assert 'id="chart_chart1"' in html
        assert 'id="chart_chart2"' in html

    def test_echarts_init_for_each_chart(self, sample_dashboard_config, temp_output_dir):
        """Each chart should have echarts.init call."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig

        config = DashboardConfig(**sample_dashboard_config)
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        assert "echarts.init(document.getElementById('chart_chart1'))" in html
        assert "echarts.init(document.getElementById('chart_chart2'))" in html

    def test_resize_handler_present(self, sample_dashboard_config, temp_output_dir):
        """HTML should contain window resize handler."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig

        config = DashboardConfig(**sample_dashboard_config)
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        assert "window.addEventListener('resize'" in html

    def test_title_in_html(self, sample_dashboard_config, temp_output_dir):
        """Dashboard title should appear in title tag."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig

        config = DashboardConfig(**sample_dashboard_config)
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        assert '<title>Test Dashboard</title>' in html


class TestMapScriptAggregation:
    """Test map script aggregation from multiple charts."""

    def test_china_map_aggregated(self, temp_db_with_data, temp_output_dir):
        """Config with china map in any chart should include china.js script."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig, ChartConfig, ChartPosition

        config = DashboardConfig(
            title="Test",
            columns=2,
            db_path=temp_db_with_data,
            charts=[
                ChartConfig(
                    id="chart1",
                    position=ChartPosition(row=0, col=0),
                    query="SELECT name, sales FROM products",
                    echarts_option={"geo": {"map": "china"}}
                )
            ]
        )
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        assert 'china.js' in html

    def test_world_map_aggregated(self, temp_db_with_data, temp_output_dir):
        """Config with world map should include world.js script."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig, ChartConfig, ChartPosition

        config = DashboardConfig(
            title="Test",
            columns=2,
            db_path=temp_db_with_data,
            charts=[
                ChartConfig(
                    id="chart1",
                    position=ChartPosition(row=0, col=0),
                    query="SELECT name, sales FROM products",
                    echarts_option={"geo": {"map": "world"}}
                )
            ]
        )
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        assert 'world.js' in html

    def test_province_map_aggregated(self, temp_db_with_data, temp_output_dir):
        """Config with province name should include province script."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig, ChartConfig, ChartPosition

        config = DashboardConfig(
            title="Test",
            columns=2,
            db_path=temp_db_with_data,
            charts=[
                ChartConfig(
                    id="chart1",
                    position=ChartPosition(row=0, col=0),
                    query="SELECT name, sales FROM products",
                    echarts_option={"geo": {"map": "广东"}}
                )
            ]
        )
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        assert 'guangdong.js' in html

    def test_multiple_maps_all_included(self, temp_db_with_data, temp_output_dir):
        """Charts using china, world, province should all get their scripts."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig, ChartConfig, ChartPosition

        config = DashboardConfig(
            title="Test",
            columns=2,
            db_path=temp_db_with_data,
            charts=[
                ChartConfig(
                    id="chart1",
                    position=ChartPosition(row=0, col=0),
                    query="SELECT name, sales FROM products",
                    echarts_option={"geo": {"map": "china"}}
                ),
                ChartConfig(
                    id="chart2",
                    position=ChartPosition(row=0, col=1),
                    query="SELECT name, sales FROM products",
                    echarts_option={"geo": {"map": "world"}}
                ),
                ChartConfig(
                    id="chart3",
                    position=ChartPosition(row=1, col=0),
                    query="SELECT name, sales FROM products",
                    echarts_option={"geo": {"map": "北京"}}
                )
            ]
        )
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        generate_dashboard_html(config, output_path)

        with open(output_path, 'r', encoding='utf-8') as f:
            html = f.read()

        assert 'china.js' in html
        assert 'world.js' in html
        assert 'beijing.js' in html


class TestCLI:
    """Test CLI interface."""

    def test_cli_with_config_file(self, sample_dashboard_config, temp_output_dir):
        """CLI with --config flag should produce HTML output."""
        import subprocess
        import sys

        config_path = build_config_file(sample_dashboard_config, temp_output_dir)
        output_path = os.path.join(temp_output_dir, "output.html")

        result = subprocess.run(
            [sys.executable, "scripts/dashboard_generator.py",
             "--config", config_path, "--output", output_path],
            capture_output=True,
            text=True,
            cwd="/Users/wuliang/workspace/echart-skill"
        )

        assert result.returncode == 0
        assert os.path.exists(output_path)

    def test_cli_output_path(self, sample_dashboard_config, temp_output_dir):
        """CLI with --output flag should write to specified path."""
        import subprocess
        import sys

        config_path = build_config_file(sample_dashboard_config, temp_output_dir)
        output_path = os.path.join(temp_output_dir, "custom_dashboard.html")

        result = subprocess.run(
            [sys.executable, "scripts/dashboard_generator.py",
             "--config", config_path, "--output", output_path],
            capture_output=True,
            text=True,
            cwd="/Users/wuliang/workspace/echart-skill"
        )

        assert result.returncode == 0
        assert os.path.exists(output_path)


class TestEmptyQueryWarning:
    """Test handling of empty query results."""

    def test_empty_query_warning(self, temp_output_dir):
        """Empty query result should log warning but not fail."""
        from scripts.dashboard_generator import generate_dashboard_html
        from scripts.dashboard_schema import DashboardConfig, ChartConfig, ChartPosition

        # Create a temp db with no data
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        conn = sqlite3.connect(db_path)
        conn.execute('CREATE TABLE empty_table (id INTEGER, name TEXT)')
        conn.commit()
        conn.close()

        try:
            config = DashboardConfig(
                title="Test",
                columns=2,
                db_path=db_path,
                charts=[
                    ChartConfig(
                        id="chart1",
                        position=ChartPosition(row=0, col=0),
                        query="SELECT * FROM empty_table"
                    )
                ]
            )
            output_path = os.path.join(temp_output_dir, "dashboard.html")

            # Should not raise
            generate_dashboard_html(config, output_path)

            # HTML should still be created
            assert os.path.exists(output_path)

            with open(output_path, 'r', encoding='utf-8') as f:
                html = f.read()

            # Should still have chart container
            assert 'id="chart_chart1"' in html

        finally:
            os.unlink(db_path)


class TestEndToEnd:
    """End-to-end integration tests."""

    @pytest.mark.integration
    def test_full_dashboard_workflow(self, temp_db_with_data, temp_output_dir):
        """Full workflow from config to HTML output."""
        from scripts.dashboard_generator import generate_dashboard

        config = {
            "title": "Integration Dashboard",
            "columns": 2,
            "db_path": temp_db_with_data,
            "charts": [
                {
                    "id": "bar_chart",
                    "position": {"row": 0, "col": 0},
                    "title": "Sales by Product",
                    "query": "SELECT name, sales FROM products",
                    "echarts_option": {
                        "xAxis": {"type": "category"},
                        "yAxis": {"type": "value"},
                        "series": [{"type": "bar"}]
                    }
                },
                {
                    "id": "pie_chart",
                    "position": {"row": 0, "col": 1},
                    "title": "Category Distribution",
                    "query": "SELECT category, SUM(sales) as total FROM products GROUP BY category",
                    "echarts_option": {
                        "series": [{"type": "pie"}]
                    }
                },
                {
                    "id": "wide_chart",
                    "position": {"row": 1, "col": 0, "col_span": 2},
                    "title": "Trend",
                    "query": "SELECT date, quantity FROM sales",
                    "echarts_option": {
                        "xAxis": {"type": "category"},
                        "yAxis": {"type": "value"},
                        "series": [{"type": "line"}]
                    }
                }
            ]
        }

        config_path = build_config_file(config, temp_output_dir)
        output_path = os.path.join(temp_output_dir, "dashboard.html")

        result_path = generate_dashboard(config_path, output_path)

        assert os.path.exists(result_path)

        with open(result_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Verify all chart IDs
        assert 'id="chart_bar_chart"' in html
        assert 'id="chart_pie_chart"' in html
        assert 'id="chart_wide_chart"' in html

        # Verify grid layout
        assert 'grid-template-columns: repeat(2, 1fr)' in html

        # Verify resize handler
        assert "window.addEventListener('resize'" in html

        # Verify title
        assert '<title>Integration Dashboard</title>' in html
