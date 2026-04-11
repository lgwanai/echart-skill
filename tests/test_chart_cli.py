"""Unit tests for chart CLI module."""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from scripts.chart_cli import (
    sanitize_filename,
    generate_default_filename,
    main,
)


class TestSanitizeFilename:
    """Tests for filename sanitization."""
    
    def test_sanitize_simple_text(self):
        """Test basic text sanitization."""
        assert sanitize_filename("My Chart") == "My_Chart"
    
    def test_sanitize_special_characters(self):
        """Test removal of special characters."""
        assert sanitize_filename("Chart/Report:2024") == "Chart_Report_2024"
    
    def test_sanitize_chinese_characters(self):
        """Test Chinese characters are preserved."""
        result = sanitize_filename("中文图表")
        assert "中文图表" in result
    
    def test_sanitize_multiple_underscores(self):
        """Test multiple underscores are collapsed."""
        assert sanitize_filename("My___Chart") == "My_Chart"
    
    def test_sanitize_empty_string(self):
        """Test empty string returns default."""
        assert sanitize_filename("") == "export"


class TestGenerateDefaultFilename:
    """Tests for default filename generation."""
    
    def test_generate_includes_title(self):
        """Test filename includes sanitized title."""
        filename = generate_default_filename("Sales Report")
        assert filename.startswith("Sales_Report_")
    
    def test_generate_includes_timestamp(self):
        """Test filename includes timestamp."""
        filename = generate_default_filename("Chart")
        assert "_" in filename
        assert filename.endswith(".html")
        parts = filename.replace("Chart_", "").replace(".html", "").split("_")
        assert len(parts) == 2
    
    def test_generate_chinese_title(self):
        """Test Chinese title in filename."""
        filename = generate_default_filename("销售报表")
        assert "销售报表" in filename


class TestCLIIntegration:
    """Integration tests for CLI commands."""
    
    @pytest.fixture
    def mock_config(self, tmp_path):
        """Create mock chart config file."""
        config = {
            "db_path": "workspace.duckdb",
            "query": "SELECT * FROM test",
            "title": "Test Chart",
            "echarts_option": {"series": [{"type": "bar"}]}
        }
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config), encoding='utf-8')
        return str(config_path)
    
    def test_cli_no_command(self, capsys):
        """Test CLI with no command shows help."""
        with pytest.raises(SystemExit) as exc:
            main()
        
        assert exc.value.code == 2
    
    def test_cli_help_flag(self, capsys):
        """Test --help shows usage."""
        with pytest.raises(SystemExit):
            sys.argv = ['chart-cli', '--help']
            main()
        
        captured = capsys.readouterr()
        assert 'export-chart' in captured.out
        assert 'export-dashboard' in captured.out
        assert 'export-gantt' in captured.out
    
    def test_cli_missing_config(self, capsys):
        """Test error when config file missing."""
        sys.argv = ['chart-cli', 'export-chart', 'nonexistent.json']
        
        with pytest.raises(SystemExit) as exc:
            main()
        
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Config file not found" in captured.err
    
    def test_cli_invalid_json(self, tmp_path, capsys):
        """Test error when config has invalid JSON."""
        bad_config = tmp_path / "bad.json"
        bad_config.write_text("{ invalid json", encoding='utf-8')
        
        sys.argv = ['chart-cli', 'export-chart', str(bad_config)]
        
        with pytest.raises(SystemExit) as exc:
            main()
        
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Invalid JSON" in captured.err
    
    @patch('scripts.chart_cli.export_standalone_chart')
    def test_export_chart_success(self, mock_export, mock_config, tmp_path):
        """Test successful chart export."""
        output_path = str(tmp_path / "output.html")
        mock_export.return_value = output_path
        
        sys.argv = ['chart-cli', 'export-chart', mock_config, '--output', output_path]
        
        with pytest.raises(SystemExit) as exc:
            main()
        
        assert exc.value.code == 0
        mock_export.assert_called_once()
    
    @patch('scripts.chart_cli.export_standalone_dashboard')
    def test_export_dashboard_success(self, mock_export, tmp_path):
        """Test successful dashboard export."""
        config = {"title": "Test Dashboard", "charts": []}
        config_path = tmp_path / "dashboard.json"
        config_path.write_text(json.dumps(config), encoding='utf-8')
        
        output_path = str(tmp_path / "output.html")
        mock_export.return_value = output_path
        
        sys.argv = ['chart-cli', 'export-dashboard', str(config_path), '--output', output_path]
        
        with pytest.raises(SystemExit) as exc:
            main()
        
        assert exc.value.code == 0
    
    @patch('scripts.chart_cli.export_standalone_gantt')
    def test_export_gantt_success(self, mock_export, tmp_path):
        """Test successful Gantt export."""
        config = {
            "title": "Project Timeline",
            "tasks": [{"name": "Task 1", "start": "2024-01-01", "end": "2024-01-10"}]
        }
        config_path = tmp_path / "gantt.json"
        config_path.write_text(json.dumps(config), encoding='utf-8')
        
        output_path = str(tmp_path / "output.html")
        mock_export.return_value = output_path
        
        sys.argv = ['chart-cli', 'export-gantt', str(config_path), '--output', output_path]
        
        with pytest.raises(SystemExit) as exc:
            main()
        
        assert exc.value.code == 0
    
    @patch('scripts.chart_cli.export_standalone_chart')
    def test_export_with_dark_theme(self, mock_export, mock_config, tmp_path):
        """Test export with dark theme."""
        output_path = str(tmp_path / "output.html")
        mock_export.return_value = output_path
        
        sys.argv = ['chart-cli', 'export-chart', mock_config, '--output', output_path, '--theme', 'dark']
        
        with pytest.raises(SystemExit):
            main()
        
        call_args = mock_export.call_args
        assert call_args[1]['theme'] == 'dark'
    
    @patch('scripts.chart_cli.export_standalone_chart')
    def test_export_default_filename(self, mock_export, mock_config, tmp_path):
        """Test that default filename is generated when --output not specified."""
        mock_export.return_value = "test_chart_20240101_120000.html"
        
        sys.argv = ['chart-cli', 'export-chart', mock_config]
        
        with pytest.raises(SystemExit):
            main()
        
        call_args = mock_export.call_args
        output_arg = call_args[0][1]
        assert "Test_Chart" in output_arg or "test_chart" in output_arg.lower()
