"""
Gantt Chart Generation Module.

Provides a simplified API for creating Gantt charts using ECharts custom series.
Users can create Gantt charts with minimal configuration by providing a task array
with name, start, and end fields.

Usage:
    from scripts.gantt_chart import generate_gantt_chart

    config = {
        "title": "Project Timeline",
        "tasks": [
            {"name": "Design", "start": "2024-01-01", "end": "2024-01-15"},
            {"name": "Development", "start": "2024-01-10", "end": "2024-02-01"},
        ]
    }
    output_path = generate_gantt_chart(config)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from pydantic import BaseModel, Field, field_validator

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_config import get_logger

logger = get_logger(__name__)


# JavaScript for renderItem function
GANTT_RENDER_ITEM_JS = """
function renderGanttItem(params, api) {
    var categoryIndex = api.value(0);
    var start = api.coord([api.value(1), categoryIndex]);
    var end = api.coord([api.value(2), categoryIndex]);
    var height = api.size([0, 1])[1] * 0.6;

    return {
        type: 'rect',
        shape: {
            x: start[0],
            y: start[1] - height / 2,
            width: end[0] - start[0],
            height: height
        },
        style: api.style({
            fill: api.value(3) || '#5470c6'
        })
    };
}
"""


class GanttTask(BaseModel):
    """Single task in a Gantt chart.

    Attributes:
        name: Task name (displayed on Y-axis)
        start: Task start time (datetime or ISO string)
        end: Task end time (datetime or ISO string)
        category: Optional category for grouping
        color: Optional custom bar color
    """

    name: str = Field(description="Task name")
    start: datetime = Field(description="Task start time")
    end: datetime = Field(description="Task end time")
    category: Optional[str] = Field(default=None, description="Optional category")
    color: Optional[str] = Field(default=None, description="Optional custom color")

    @field_validator("start", "end", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> datetime:
        """Parse datetime from string or return datetime object.

        Args:
            v: Input value (datetime or ISO string)

        Returns:
            datetime object

        Raises:
            ValueError: If string cannot be parsed as datetime
        """
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Handle ISO format strings
            # Replace Z suffix with +00:00 for UTC
            v = v.replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                # Try simple date format
                return datetime.strptime(v, "%Y-%m-%d")
        raise ValueError(f"Cannot parse {type(v)} as datetime")

    @field_validator("end")
    @classmethod
    def end_after_start(cls, v: datetime, info) -> datetime:
        """Validate that end time is after start time.

        Args:
            v: End time value
            info: Validation context with access to other fields

        Returns:
            Validated end time

        Raises:
            ValueError: If end is not after start
        """
        if "start" in info.data and v <= info.data["start"]:
            task_name = info.data.get("name", "unknown")
            raise ValueError(
                f"Task '{task_name}': end time must be after start time"
            )
        return v


class GanttChartConfig(BaseModel):
    """Gantt chart configuration.

    Attributes:
        title: Chart title
        tasks: List of Gantt tasks
        output_path: Optional output file path
    """

    title: str = Field(default="Gantt Chart", description="Chart title")
    tasks: list[GanttTask] = Field(min_length=1, description="List of Gantt tasks")
    output_path: Optional[str] = Field(
        default=None, description="Optional output file path"
    )


def generate_gantt_chart(config: dict) -> str:
    """Generate a Gantt chart from simplified task configuration.

    Args:
        config: Dict with 'title', 'tasks' list, optional 'output_path'
            - title: str (default "Gantt Chart")
            - tasks: list of dicts with 'name', 'start', 'end', optional 'color'
            - output_path: optional str for output file path

    Returns:
        Path to generated HTML file
    """
    # Import here to avoid circular import issues
    from scripts.chart_generator import generate_echarts_html

    # Validate config
    gantt_config = GanttChartConfig(**config)

    # Extract unique task names for Y-axis categories (preserve order)
    task_names = list(dict.fromkeys(task.name for task in gantt_config.tasks))

    # Calculate date range with padding
    all_dates = []
    for task in gantt_config.tasks:
        all_dates.extend([task.start, task.end])

    min_date = min(all_dates) - timedelta(days=1)
    max_date = max(all_dates) + timedelta(days=1)

    # Build series data: [categoryIndex, startTime, endTime, color]
    series_data = []
    for task in gantt_config.tasks:
        category_index = task_names.index(task.name)
        series_data.append([
            category_index,
            task.start.isoformat(),
            task.end.isoformat(),
            task.color,
        ])

    # Build ECharts option
    echarts_option = {
        "title": {"text": gantt_config.title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "xAxis": {
            "type": "time",
            "position": "top",
            "min": min_date.isoformat(),
            "max": max_date.isoformat(),
        },
        "yAxis": {"type": "category", "data": task_names, "inverse": True},
        "series": [
            {
                "type": "custom",
                "renderItem": "__renderGanttItem__",  # Placeholder, replaced in custom_js
                "encode": {"x": [1, 2], "y": 0},
                "data": series_data,
            }
        ],
    }

    # Prepare custom JS with renderItem function
    # Replace placeholder with actual function reference
    custom_js = GANTT_RENDER_ITEM_JS.replace(
        "function renderGanttItem", "var __renderGanttItem__ = function"
    )

    # Determine output path
    output_path = gantt_config.output_path
    if not output_path:
        base_dir = Path(__file__).parent.parent
        output_path = str(base_dir / "outputs" / "html" / "gantt_chart.html")

    # Empty DataFrame since data is in echarts_option
    df = pd.DataFrame()

    # Generate HTML using existing infrastructure
    generate_echarts_html(
        df,
        {"title": gantt_config.title, "echarts_option": echarts_option, "custom_js": custom_js},
        output_path,
    )

    logger.info("Gantt chart generated", output_path=output_path, tasks=len(gantt_config.tasks))
    return output_path


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(description="Gantt Chart Generator")
    parser.add_argument(
        "--config",
        required=True,
        help="JSON string or path to JSON file containing Gantt configuration",
    )

    args = parser.parse_args()

    try:
        if os.path.isfile(args.config):
            with open(args.config, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = json.loads(args.config)

        result = generate_gantt_chart(config)
        print(f"Gantt chart generated: {result}")
    except Exception as e:
        logger.error("Gantt chart generation failed", error=str(e))
        raise
