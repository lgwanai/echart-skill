"""
Simplified Dashboard Generator.

Provides natural-language-friendly dashboard generation with:
- Auto layout algorithm
- Simplified chart config (no need to write SQL or ECharts option)
- Template-based generation
- Smart chart suggestion

Usage:
    from scripts.simple_dashboard import SimpleDashboard
    
    dashboard = SimpleDashboard(
        title="销售分析",
        db_path="workspace.duckdb",
        charts=[
            {"type": "bar", "title": "地区销售", "group_by": "region"},
            {"type": "pie", "title": "品类占比", "group_by": "category"},
            {"type": "line", "title": "月度趋势", "time_column": "month"},
            {"type": "map", "title": "全国分布", "geo_column": "province"}
        ]
    )
    
    dashboard.generate("outputs/html/dashboard.html")
"""

import json
import os
import re
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.dashboard_generator import generate_dashboard_html
from scripts.dashboard_schema import DashboardConfig, ChartConfig, ChartPosition
from database import get_repository


class SimpleChartSpec:
    """Simplified chart specification."""
    
    def __init__(
        self,
        chart_type: str,
        title: str,
        table: str = None,
        group_by: str = None,
        agg_column: str = None,
        time_column: str = None,
        geo_column: str = None,
        value_column: str = None,
        top_n: int = None,
        filter: str = None,
        sort: str = "desc",
        custom_config: dict = None
    ):
        self.chart_type = chart_type
        self.title = title
        self.table = table
        self.group_by = group_by
        self.agg_column = agg_column
        self.time_column = time_column
        self.geo_column = geo_column
        self.value_column = value_column or agg_column
        self.top_n = top_n
        self.filter = filter
        self.sort = sort
        self.custom_config = custom_config or {}
    
    def to_dict(self):
        return {
            "chart_type": self.chart_type,
            "title": self.title,
            "table": self.table,
            "group_by": self.group_by,
            "agg_column": self.agg_column,
            "time_column": self.time_column,
            "geo_column": self.geo_column,
            "value_column": self.value_column,
            "top_n": self.top_n,
            "filter": self.filter,
            "sort": self.sort,
            "custom_config": self.custom_config
        }


class SimpleDashboard:
    """Simplified dashboard generator with natural language support."""
    
    # Chart type templates
    CHART_TEMPLATES = {
        "bar": {
            "echarts_option": {
                "xAxis": {"type": "category"},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar"}]
            },
            "custom_js_template": "option.series[0].data = rawData.map(r => r.value); option.xAxis.data = rawData.map(r => r.{group_by});"
        },
        "line": {
            "echarts_option": {
                "xAxis": {"type": "category"},
                "yAxis": {"type": "value"},
                "series": [{"type": "line", "smooth": True}]
            },
            "custom_js_template": "option.series[0].data = rawData.map(r => r.value); option.xAxis.data = rawData.map(r => r.{group_by});"
        },
        "pie": {
            "echarts_option": {
                "series": [{"type": "pie", "radius": ["40%", "70%"]}]
            },
            "custom_js_template": "option.series[0].data = rawData.map(r => ({name: r.{group_by}, value: r.value}));"
        },
        "map": {
            "echarts_option": {
                "visualMap": {
                    "min": 0,
                    "max": 100000,
                    "left": "left",
                    "top": "bottom",
                    "text": ["高", "低"],
                    "calculable": True,
                    "inRange": {"color": ["#f7fbff", "#08306b"]}
                },
                "series": [{
                    "type": "map",
                    "map": "china",
                    "roam": True,
                    "data": []
                }]
            },
            "custom_js_template": "option.series[0].data = rawData.map(r => ({name: r.{geo_column}, value: r.value})); option.visualMap.max = Math.max(...rawData.map(r => r.value));"
        },
        "scatter": {
            "echarts_option": {
                "xAxis": {"type": "value"},
                "yAxis": {"type": "value"},
                "series": [{"type": "scatter"}]
            },
            "custom_js_template": "option.series[0].data = rawData.map(r => [r.x, r.y]);"
        },
        "radar": {
            "echarts_option": {
                "radar": {"indicator": []},
                "series": [{"type": "radar"}]
            },
            "custom_js_template": "option.radar.indicator = rawData.columns.filter(c => c !== 'name').map(c => ({name: c, max: 100}));"
        },
        "funnel": {
            "echarts_option": {
                "series": [{"type": "funnel"}]
            },
            "custom_js_template": "option.series[0].data = rawData.map(r => ({name: r.{group_by}, value: r.value}));"
        },
        "treemap": {
            "echarts_option": {
                "series": [{"type": "treemap"}]
            },
            "custom_js_template": "option.series[0].data = rawData.map(r => ({name: r.{group_by}, value: r.value}));"
        },
        "sunburst": {
            "echarts_option": {
                "series": [{"type": "sunburst"}]
            },
            "custom_js_template": "option.series[0].data = rawData;"
        }
    }
    
    def __init__(
        self,
        title: str,
        db_path: str = "workspace.duckdb",
        table: str = None,
        charts: list = None,
        layout: str = "auto",
        columns: int = None
    ):
        self.title = title
        self.db_path = db_path
        self.table = table
        self.charts = charts or []
        self.layout = layout
        self.columns = columns
        
    def _detect_table(self):
        """Auto-detect the main table if not specified."""
        if self.table:
            return self.table
        
        repo = get_repository(self.db_path)
        with repo.connection() as conn:
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            
        if not tables:
            raise ValueError("No tables found in database")
        
        if len(tables) == 1:
            return tables[0][0]
        
        # Return the largest table
        sizes = []
        with repo.connection() as conn:
            for (t,) in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {self._quote_id(t)}").fetchone()[0]
                sizes.append((t, count))
        return max(sizes, key=lambda x: x[1])[0]
    
    @staticmethod
    def _validate_identifier(name: str, context: str = "identifier") -> str:
        """Validate that a name is a safe SQL identifier."""
        if not name or not isinstance(name, str):
            raise ValueError(f"Invalid {context}: {name!r}")
        stripped = name.replace('_', '').replace('-', '')
        if not stripped or not stripped.isalnum():
            raise ValueError(f"Unsafe {context} (special chars): {name!r}")
        return name
    
    # Allowed filter operators (whitelist: column operator value, no semicolons/comments)
    _FILTER_PATTERN = re.compile(
        r'^[\w\u4e00-\u9fff]+'                # column name
        r'\s*(=|!=|<|>|<=|>=|LIKE|IN|NOT IN)\s*'  # operator
        r'[^;\'"\-]+$',                        # value (no semicolons, quotes, or double-dash)
        re.IGNORECASE
    )
    
    @staticmethod
    def _quote_id(name: str) -> str:
        """Quote an identifier for DuckDB."""
        return f'"{name}"'
    
    def _build_query(self, spec: SimpleChartSpec, table: str) -> str:
        """Build SQL query from simplified spec with safe identifier quoting."""
        
        # Validate and quote identifiers
        table = self._quote_id(self._validate_identifier(table, "table"))
        
        group_by = spec.group_by or spec.time_column or spec.geo_column
        if not group_by:
            raise ValueError("At least one of group_by, time_column, or geo_column must be specified")
        
        group_by = self._validate_identifier(group_by, "group_by")
        group_by_q = self._quote_id(group_by)
        
        agg_col = spec.agg_column or spec.value_column
        
        # Build SELECT clause
        if agg_col:
            agg_col = self._validate_identifier(agg_col, "agg_column")
            agg_col_q = self._quote_id(agg_col)
            select = f"{group_by_q}, SUM({agg_col_q}) as value"
        else:
            select = f"{group_by_q}, COUNT(*) as value"
        
        # Build query
        query = f"SELECT {select} FROM {table}"
        
        # Add filter (validated against whitelist pattern)
        if spec.filter:
            filter_str = spec.filter.strip()
            if not filter_str:
                raise ValueError("filter cannot be empty")
            if not self._FILTER_PATTERN.match(filter_str):
                raise ValueError(f"Unsafe filter expression: {filter_str!r}")
            query += f" WHERE {filter_str}"
        
        # Add GROUP BY
        query += f" GROUP BY {group_by_q}"
        
        # Add ORDER BY (whitelist sort direction)
        sort_dir = spec.sort.upper()
        if sort_dir not in ('ASC', 'DESC'):
            raise ValueError(f"sort must be 'asc' or 'desc', got: {spec.sort!r}")
        query += f" ORDER BY value {sort_dir}"
        
        # Add LIMIT
        if spec.top_n:
            if not isinstance(spec.top_n, int) or spec.top_n <= 0:
                raise ValueError(f"top_n must be a positive integer, got: {spec.top_n!r}")
            query += f" LIMIT {spec.top_n}"
        
        return query
    
    def _build_echarts_option(self, spec: SimpleChartSpec) -> tuple[dict, str]:
        """Build ECharts option and custom JS from simplified spec."""
        
        template = self.CHART_TEMPLATES.get(spec.chart_type)
        if not template:
            raise ValueError(f"Unsupported chart type: {spec.chart_type}")
        
        # Start with template
        option = template["echarts_option"].copy()
        custom_js_template = template["custom_js_template"]
        
        # Add title
        option["title"] = {"text": spec.title, "left": "center"}
        
        # Add tooltip
        option["tooltip"] = {"trigger": "axis" if spec.chart_type in ["bar", "line"] else "item"}
        
        # Replace placeholders in custom_js
        group_by = spec.group_by or spec.time_column or spec.geo_column
        custom_js = custom_js_template.replace("{group_by}", group_by).replace("{geo_column}", spec.geo_column or group_by)
        
        # Apply custom config
        if spec.custom_config:
            option.update(spec.custom_config)
        
        return option, custom_js
    
    def _auto_layout(self, num_charts: int) -> list[ChartPosition]:
        """Auto-generate positions for charts."""
        
        if num_charts == 0:
            return []
        
        if self.columns:
            cols = self.columns
        else:
            # Auto-detect columns based on chart count
            if num_charts <= 2:
                cols = 2
            elif num_charts <= 4:
                cols = 2
            elif num_charts <= 6:
                cols = 3
            else:
                cols = 3
        
        positions = []
        row = 0
        col = 0
        
        for i, spec in enumerate(self.charts):
            # Determine span based on chart type
            if spec.chart_type == "map":
                # Map should be larger
                col_span = 2
                row_span = 1
            elif spec.chart_type == "pie":
                # Pie can span vertically
                col_span = 1
                row_span = 2 if i == len(self.charts) - 1 else 1
            elif spec.chart_type in ["line", "bar"]:
                # Bar/line charts can be wider
                col_span = 2 if cols == 3 else 1
                row_span = 1
            else:
                col_span = 1
                row_span = 1
            
            # Check if we need to wrap to next row
            if col + col_span > cols:
                row += 1
                col = 0
            
            positions.append(ChartPosition(row=row, col=col, col_span=col_span, row_span=row_span))
            
            # Move to next position
            col += col_span
            if col >= cols:
                row += 1
                col = 0
        
        return positions
    
    def generate(self, output_path: str) -> str:
        """Generate dashboard HTML from simplified specs."""
        
        if not self.charts:
            raise ValueError("No charts specified. Add charts with add_chart() or from_description() before generating.")
        
        # Auto-detect table if not specified
        table = self._detect_table()
        
        # Build chart configs
        chart_configs = []
        positions = self._auto_layout(len(self.charts))
        
        for i, spec in enumerate(self.charts):
            if isinstance(spec, dict):
                spec = SimpleChartSpec(**spec)
            
            # Build query
            query = self._build_query(spec, spec.table or table)
            
            # Build ECharts option
            echarts_option, custom_js = self._build_echarts_option(spec)
            
            # Create ChartConfig
            chart_config = ChartConfig(
                id=f"chart_{i}",
                position=positions[i],
                title=spec.title,
                query=query,
                echarts_option=echarts_option,
                custom_js=custom_js
            )
            chart_configs.append(chart_config)
        
        # Determine columns and row_height
        if not self.columns:
            self.columns = max(p.col + p.col_span for p in positions)
        
        # Create DashboardConfig
        dashboard_config = DashboardConfig(
            title=self.title,
            columns=self.columns,
            row_height=400,
            gap=24,
            charts=chart_configs,
            db_path=self.db_path
        )
        
        # Generate HTML
        return generate_dashboard_html(dashboard_config, output_path)
    
    def add_chart(
        self,
        chart_type: str,
        title: str,
        group_by: str = None,
        agg_column: str = None,
        **kwargs
    ):
        """Add a chart to the dashboard."""
        spec = SimpleChartSpec(
            chart_type=chart_type,
            title=title,
            group_by=group_by,
            agg_column=agg_column,
            **kwargs
        )
        self.charts.append(spec)
        return self
    
    def from_description(self, description: str) -> "SimpleDashboard":
        """Create dashboard from natural language description.
        
        Example:
            "创建一个销售分析仪表盘，包含：
            - 各地区销售柱状图
            - 产品类别饼图
            - 月度销售趋势线图
            - 全国销售地图"
        """
        # Parse description and create charts
        lines = description.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('创建') or line.startswith('包含'):
                continue
            
            # Parse chart description
            # Format: "- 地区销售柱状图" or "- 各地区销售 (柱状图)"
            
            # Try to extract chart type
            chart_types = ["柱状图", "折线图", "饼图", "地图", "散点图", "雷达图", "漏斗图", "树图", "旭日图"]
            chart_type_map = {
                "柱状图": "bar",
                "折线图": "line",
                "饼图": "pie",
                "地图": "map",
                "散点图": "scatter",
                "雷达图": "radar",
                "漏斗图": "funnel",
                "树图": "treemap",
                "旭日图": "sunburst"
            }
            
            detected_type = None
            for cn_type, en_type in chart_type_map.items():
                if cn_type in line:
                    detected_type = en_type
                    break
            
            if not detected_type:
                continue
            
            # Extract title (remove chart type)
            title = re.sub(r'[（(].*?[）)]|柱状图|折线图|饼图|地图|散点图|雷达图|漏斗图|树图|旭日图', '', line)
            title = title.strip().lstrip('-').strip()
            
            if title:
                self.add_chart(chart_type=detected_type, title=title)
        
        return self


# Convenience functions
def create_dashboard_from_text(
    description: str,
    db_path: str = "workspace.duckdb",
    output_path: str = None,
    title: str = None
) -> str:
    """Create dashboard from natural language description.
    
    Args:
        description: Natural language description of the dashboard
        db_path: Database path
        output_path: Output HTML path
        title: Dashboard title (extracted from description if not provided)
    
    Returns:
        Path to generated dashboard HTML
    
    Example:
        create_dashboard_from_text(
            "创建销售分析仪表盘，包含：
            - 各地区销售柱状图
            - 产品类别饼图  
            - 月度趋势折线图
            - 全国分布地图",
            db_path="workspace.duckdb",
            output_path="outputs/html/dashboard.html"
        )
    """
    # Extract title from first line if not provided
    if not title:
        lines = description.strip().split('\n')
        first_line = lines[0] if lines else "Dashboard"
        title = re.sub(r'创建|仪表盘|，|包含', '', first_line).strip() or "Dashboard"
    
    dashboard = SimpleDashboard(title=title, db_path=db_path)
    dashboard.from_description(description)
    
    # Auto-generate output path if not provided
    if not output_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_dir, "outputs", "html", f"{title}_dashboard.html")
    
    return dashboard.generate(output_path)


def create_sales_dashboard_example(db_path: str = "workspace.duckdb", output_path: str = None) -> str:
    """Create a typical sales analysis dashboard."""
    dashboard = SimpleDashboard(
        title="销售数据分析",
        db_path=db_path
    )
    
    dashboard.add_chart("bar", "各地区销售额", group_by="region")
    dashboard.add_chart("pie", "产品类别占比", group_by="category")
    dashboard.add_chart("line", "月度销售趋势", time_column="month")
    dashboard.add_chart("map", "全国销售分布", geo_column="province")
    
    if not output_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_dir, "outputs", "html", "sales_dashboard.html")
    
    return dashboard.generate(output_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Dashboard Generator")
    parser.add_argument("--description", type=str, help="Natural language description of dashboard")
    parser.add_argument("--db", type=str, default="workspace.duckdb", help="Database path")
    parser.add_argument("--output", type=str, help="Output HTML path")
    parser.add_argument("--title", type=str, help="Dashboard title")
    parser.add_argument("--example", action="store_true", help="Generate example sales dashboard")
    
    args = parser.parse_args()
    
    if args.example:
        output = create_sales_dashboard_example(args.db, args.output)
        print(f"✅ Dashboard generated: {output}")
    elif args.description:
        output = create_dashboard_from_text(
            args.description,
            args.db,
            args.output,
            args.title
        )
        print(f"✅ Dashboard generated: {output}")
    else:
        parser.print_help()