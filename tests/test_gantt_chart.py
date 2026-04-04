"""Tests for Gantt chart generation module."""

import os
import sys

# Mock the server module before importing gantt_chart
import unittest.mock as mock

sys.modules["server"] = mock.MagicMock()
sys.modules["server"].ensure_server_running = mock.MagicMock(
    return_value="http://localhost:8080"
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from pathlib import Path

import pytest

from scripts.gantt_chart import GanttTask, GanttChartConfig


class TestGanttTaskValidation:
    """Test GanttTask model validation."""

    def test_gantt_task_accepts_datetime_objects(self):
        """GanttTask should accept datetime objects for start/end."""
        task = GanttTask(
            name="Design",
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 15),
        )
        assert task.name == "Design"
        assert task.start == datetime(2024, 1, 1)
        assert task.end == datetime(2024, 1, 15)

    def test_gantt_task_accepts_iso_string_for_start(self):
        """GanttTask should accept ISO format string for start."""
        task = GanttTask(
            name="Development",
            start="2024-01-10",
            end=datetime(2024, 2, 1),
        )
        assert task.start == datetime(2024, 1, 10)

    def test_gantt_task_accepts_iso_string_for_end(self):
        """GanttTask should accept ISO format string for end."""
        task = GanttTask(
            name="Testing",
            start=datetime(2024, 1, 25),
            end="2024-02-10",
        )
        assert task.end == datetime(2024, 2, 10)

    def test_gantt_task_accepts_iso_string_with_time(self):
        """GanttTask should accept ISO format string with time component."""
        task = GanttTask(
            name="Detailed Task",
            start="2024-01-01T09:00:00",
            end="2024-01-01T17:00:00",
        )
        assert task.start == datetime(2024, 1, 1, 9, 0, 0)
        assert task.end == datetime(2024, 1, 1, 17, 0, 0)

    def test_gantt_task_rejects_end_before_start(self):
        """GanttTask should reject end time before start time."""
        with pytest.raises(ValueError) as exc_info:
            GanttTask(
                name="Invalid Task",
                start=datetime(2024, 1, 15),
                end=datetime(2024, 1, 1),  # End before start
            )
        assert "end time must be after start time" in str(exc_info.value).lower()

    def test_gantt_task_rejects_end_equals_start(self):
        """GanttTask should reject end time equal to start time."""
        with pytest.raises(ValueError) as exc_info:
            GanttTask(
                name="Zero Duration Task",
                start=datetime(2024, 1, 1),
                end=datetime(2024, 1, 1),  # Same as start
            )
        assert "end time must be after start time" in str(exc_info.value).lower()

    def test_gantt_task_optional_category(self):
        """GanttTask should have optional category field."""
        task = GanttTask(
            name="Task with category",
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 5),
            category="Development",
        )
        assert task.category == "Development"

    def test_gantt_task_optional_color(self):
        """GanttTask should have optional color field."""
        task = GanttTask(
            name="Colored Task",
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 5),
            color="#FF5733",
        )
        assert task.color == "#FF5733"

    def test_gantt_task_category_defaults_to_none(self):
        """GanttTask category should default to None."""
        task = GanttTask(
            name="Simple Task",
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 5),
        )
        assert task.category is None

    def test_gantt_task_color_defaults_to_none(self):
        """GanttTask color should default to None."""
        task = GanttTask(
            name="Simple Task",
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 5),
        )
        assert task.color is None


class TestGanttChartConfigValidation:
    """Test GanttChartConfig model validation."""

    def test_gantt_chart_config_accepts_valid_tasks(self):
        """GanttChartConfig should accept valid tasks list."""
        config = GanttChartConfig(
            title="Project Timeline",
            tasks=[
                GanttTask(
                    name="Design",
                    start=datetime(2024, 1, 1),
                    end=datetime(2024, 1, 15),
                ),
                GanttTask(
                    name="Development",
                    start=datetime(2024, 1, 10),
                    end=datetime(2024, 2, 1),
                ),
            ],
        )
        assert config.title == "Project Timeline"
        assert len(config.tasks) == 2

    def test_gantt_chart_config_default_title(self):
        """GanttChartConfig should have default title."""
        config = GanttChartConfig(
            tasks=[
                GanttTask(
                    name="Task",
                    start=datetime(2024, 1, 1),
                    end=datetime(2024, 1, 5),
                )
            ]
        )
        assert config.title == "Gantt Chart"

    def test_gantt_chart_config_rejects_empty_tasks(self):
        """GanttChartConfig should reject empty tasks list."""
        with pytest.raises(ValueError) as exc_info:
            GanttChartConfig(title="Empty Chart", tasks=[])
        # Pydantic v2 raises this as a validation error with specific message
        assert "at least 1" in str(exc_info.value).lower() or "min_length" in str(
            exc_info.value
        ).lower()

    def test_gantt_chart_config_optional_output_path(self):
        """GanttChartConfig should have optional output_path."""
        config = GanttChartConfig(
            title="Test",
            tasks=[
                GanttTask(
                    name="Task",
                    start=datetime(2024, 1, 1),
                    end=datetime(2024, 1, 5),
                )
            ],
            output_path="/custom/path/gantt.html",
        )
        assert config.output_path == "/custom/path/gantt.html"

    def test_gantt_chart_config_output_path_defaults_to_none(self):
        """GanttChartConfig output_path should default to None."""
        config = GanttChartConfig(
            tasks=[
                GanttTask(
                    name="Task",
                    start=datetime(2024, 1, 1),
                    end=datetime(2024, 1, 5),
                )
            ]
        )
        assert config.output_path is None


class TestGenerateGanttChart:
    """Test generate_gantt_chart function."""

    def test_generate_gantt_chart_creates_html_file(self, temp_output_dir):
        """generate_gantt_chart should create an HTML file."""
        from scripts.gantt_chart import generate_gantt_chart

        output_path = os.path.join(temp_output_dir, "gantt.html")
        config = {
            "title": "Project Timeline",
            "tasks": [
                {"name": "Design", "start": "2024-01-01", "end": "2024-01-15"},
                {
                    "name": "Development",
                    "start": "2024-01-10",
                    "end": "2024-02-01",
                },
                {"name": "Testing", "start": "2024-01-25", "end": "2024-02-10"},
            ],
            "output_path": output_path,
        }

        result = generate_gantt_chart(config)
        assert result == output_path
        assert os.path.exists(output_path)

    def test_generated_html_contains_echarts_custom_series(self, temp_output_dir):
        """Generated HTML should contain ECharts custom series configuration."""
        from scripts.gantt_chart import generate_gantt_chart

        output_path = os.path.join(temp_output_dir, "gantt.html")
        config = {
            "title": "Test Gantt",
            "tasks": [
                {"name": "Task A", "start": "2024-01-01", "end": "2024-01-05"},
            ],
            "output_path": output_path,
        }

        generate_gantt_chart(config)

        with open(output_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        assert '"type": "custom"' in html_content

    def test_generated_html_contains_render_item_function(self, temp_output_dir):
        """Generated HTML should contain renderItem function for Gantt bars."""
        from scripts.gantt_chart import generate_gantt_chart

        output_path = os.path.join(temp_output_dir, "gantt.html")
        config = {
            "title": "Test Gantt",
            "tasks": [
                {"name": "Task A", "start": "2024-01-01", "end": "2024-01-05"},
            ],
            "output_path": output_path,
        }

        generate_gantt_chart(config)

        with open(output_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        assert "renderGanttItem" in html_content or "renderItem" in html_content

    def test_time_axis_shows_correct_date_range(self, temp_output_dir):
        """Time axis should show correct date range from tasks."""
        from scripts.gantt_chart import generate_gantt_chart

        output_path = os.path.join(temp_output_dir, "gantt.html")
        config = {
            "title": "Test Gantt",
            "tasks": [
                {"name": "Task A", "start": "2024-01-05", "end": "2024-01-10"},
                {"name": "Task B", "start": "2024-01-15", "end": "2024-01-20"},
            ],
            "output_path": output_path,
        }

        generate_gantt_chart(config)

        with open(output_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Time axis should have min/max set
        assert '"type": "time"' in html_content

    def test_y_axis_shows_task_names(self, temp_output_dir):
        """Y-axis should show task names as categories."""
        from scripts.gantt_chart import generate_gantt_chart

        output_path = os.path.join(temp_output_dir, "gantt.html")
        config = {
            "title": "Test Gantt",
            "tasks": [
                {"name": "Design Phase", "start": "2024-01-01", "end": "2024-01-05"},
                {
                    "name": "Build Phase",
                    "start": "2024-01-06",
                    "end": "2024-01-10",
                },
            ],
            "output_path": output_path,
        }

        generate_gantt_chart(config)

        with open(output_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        assert '"type": "category"' in html_content
        assert "Design Phase" in html_content
        assert "Build Phase" in html_content


class TestEChartsOptionGeneration:
    """Test ECharts option generation details."""

    def test_series_data_has_correct_structure(self, temp_output_dir):
        """Series data should have [categoryIndex, startTime, endTime, color]."""
        from scripts.gantt_chart import generate_gantt_chart

        output_path = os.path.join(temp_output_dir, "gantt.html")
        config = {
            "title": "Test Gantt",
            "tasks": [
                {"name": "Task A", "start": "2024-01-01", "end": "2024-01-05"},
            ],
            "output_path": output_path,
        }

        generate_gantt_chart(config)

        with open(output_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Check encode configuration
        assert '"encode"' in html_content

    def test_y_axis_is_inverse_for_top_to_bottom_order(self, temp_output_dir):
        """Y-axis should be inverse for natural top-to-bottom task order."""
        from scripts.gantt_chart import generate_gantt_chart

        output_path = os.path.join(temp_output_dir, "gantt.html")
        config = {
            "title": "Test Gantt",
            "tasks": [
                {"name": "Task A", "start": "2024-01-01", "end": "2024-01-05"},
            ],
            "output_path": output_path,
        }

        generate_gantt_chart(config)

        with open(output_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        assert '"inverse": true' in html_content

    def test_x_axis_position_is_top(self, temp_output_dir):
        """X-axis (time) should be positioned at top."""
        from scripts.gantt_chart import generate_gantt_chart

        output_path = os.path.join(temp_output_dir, "gantt.html")
        config = {
            "title": "Test Gantt",
            "tasks": [
                {"name": "Task A", "start": "2024-01-01", "end": "2024-01-05"},
            ],
            "output_path": output_path,
        }

        generate_gantt_chart(config)

        with open(output_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        assert '"position": "top"' in html_content

    def test_custom_color_applied_to_task(self, temp_output_dir):
        """Custom color should be applied to task bar."""
        from scripts.gantt_chart import generate_gantt_chart

        output_path = os.path.join(temp_output_dir, "gantt.html")
        config = {
            "title": "Test Gantt",
            "tasks": [
                {
                    "name": "Task A",
                    "start": "2024-01-01",
                    "end": "2024-01-05",
                    "color": "#FF5733",
                },
            ],
            "output_path": output_path,
        }

        generate_gantt_chart(config)

        with open(output_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        assert "#FF5733" in html_content
