"""Unit tests for Gantt chart export functionality."""

import tempfile
from pathlib import Path

import pytest

from scripts.gantt_chart import export_standalone_gantt


class TestGanttExport:
    """Tests for Gantt chart export."""
    
    def test_export_gantt_creates_html(self, tmp_path):
        """Test that export creates valid HTML file."""
        output_path = tmp_path / "gantt.html"
        
        config = {
            "title": "Project Timeline",
            "tasks": [
                {"name": "Design", "start": "2024-01-01", "end": "2024-01-15"},
                {"name": "Development", "start": "2024-01-10", "end": "2024-02-01"},
            ]
        }
        
        result = export_standalone_gantt(config, str(output_path))
        
        assert output_path.exists()
        assert result == str(output_path.absolute())
    
    def test_export_gantt_contains_echarts(self, tmp_path):
        """Test that exported HTML contains ECharts library."""
        output_path = tmp_path / "gantt.html"
        
        config = {
            "title": "Timeline",
            "tasks": [
                {"name": "Task A", "start": "2024-01-01", "end": "2024-01-10"},
            ]
        }
        
        export_standalone_gantt(config, str(output_path))
        
        html = output_path.read_text(encoding='utf-8')
        
        assert "echarts" in html.lower()
        assert "echarts.init" in html
    
    def test_export_gantt_contains_render_item(self, tmp_path):
        """Test that exported HTML contains Gantt renderItem function."""
        output_path = tmp_path / "gantt.html"
        
        config = {
            "title": "Timeline",
            "tasks": [
                {"name": "Task A", "start": "2024-01-01", "end": "2024-01-10"},
            ]
        }
        
        export_standalone_gantt(config, str(output_path))
        
        html = output_path.read_text(encoding='utf-8')
        
        assert "__renderGanttItem__" in html
        assert "renderGanttItem" in html or "renderItem" in html
    
    def test_export_gantt_with_custom_colors(self, tmp_path):
        """Test Gantt chart with custom task colors."""
        output_path = tmp_path / "gantt.html"
        
        config = {
            "title": "Colored Timeline",
            "tasks": [
                {"name": "Design", "start": "2024-01-01", "end": "2024-01-15", "color": "#ff0000"},
                {"name": "Development", "start": "2024-01-10", "end": "2024-02-01", "color": "#00ff00"},
            ]
        }
        
        export_standalone_gantt(config, str(output_path))
        
        html = output_path.read_text(encoding='utf-8')
        
        assert "#ff0000" in html
        assert "#00ff00" in html
    
    def test_export_gantt_chinese_characters(self, tmp_path):
        """Test Chinese characters are preserved."""
        output_path = tmp_path / "gantt.html"
        
        config = {
            "title": "项目时间线",
            "tasks": [
                {"name": "设计阶段", "start": "2024-01-01", "end": "2024-01-15"},
                {"name": "开发阶段", "start": "2024-01-10", "end": "2024-02-01"},
            ]
        }
        
        export_standalone_gantt(config, str(output_path))
        
        html = output_path.read_text(encoding='utf-8')
        
        assert "项目时间线" in html
        assert "设计阶段" in html
        assert "开发阶段" in html
    
    def test_export_gantt_with_theme(self, tmp_path):
        """Test Gantt chart export with dark theme."""
        output_path = tmp_path / "gantt.html"
        
        config = {
            "title": "Dark Theme Timeline",
            "tasks": [
                {"name": "Task A", "start": "2024-01-01", "end": "2024-01-10"},
            ]
        }
        
        export_standalone_gantt(config, str(output_path), theme="dark")
        
        html = output_path.read_text(encoding='utf-8')
        
        assert "#1a1a1a" in html
