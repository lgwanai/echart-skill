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
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.chart_generator import generate_echarts_html
from scripts.dashboard_generator import generate_dashboard_html
from scripts.dashboard_schema import DashboardConfig, ChartConfig, ChartPosition
from database import get_repository
import pandas as pd


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
        tables = repo.list_tables()
        
        if len(tables) == 1:
            return tables[0]
        elif len(tables) > 1:
            # Return the largest table
            sizes = [(t, repo.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]) for t in tables]
            return max(sizes, key=lambda x: x[1])[0]
        
        raise ValueError("No tables found in database")
    
    def _build_query(self, spec: SimpleChartSpec, table: str) -> str:
        """Build SQL query from simplified spec."""
        
        # Determine group_by column
        group_by = spec.group_by or spec.time_column or spec.geo_column
        
        # Determine aggregation column
        agg_col = spec.agg_column or spec.value_column
        
        # Build SELECT clause
        if agg_col:
            select = f"{group_by}, SUM({agg_col}) as value"
        else:
            select = f"{group_by}, COUNT(*) as value"
        
        # Build query
        query = f"SELECT {select} FROM {table}"
        
        # Add filter
        if spec.filter:
            query += f" WHERE {spec.filter}"
        
        # Add GROUP BY
        query += f" GROUP BY {group_by}"
        
        # Add ORDER BY
        query += f" ORDER BY value {spec.sort}"
        
        # Add LIMIT
        if spec.top_n:
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
            import re
            
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
        import re
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