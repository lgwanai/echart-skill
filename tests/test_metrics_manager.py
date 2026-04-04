import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMetricsManager:
    """Tests for metrics_manager module."""

    def test_import_metrics_manager(self):
        """Module should be importable."""
        from scripts import metrics_manager
        assert metrics_manager is not None

    def test_add_metric_function(self, tmp_path):
        """add_metric should create metric file."""
        from scripts.metrics_manager import add_metric

        metric_file = tmp_path / "metrics.md"
        add_metric("Test Metric", "Test description", str(metric_file))

        assert metric_file.exists()
        content = metric_file.read_text(encoding='utf-8')
        assert "Test Metric" in content
        assert "Test description" in content

    def test_add_metric_creates_header(self, tmp_path):
        """First metric should create file with header."""
        from scripts.metrics_manager import add_metric

        metric_file = tmp_path / "new_metrics.md"
        add_metric("First Metric", "Description", str(metric_file))

        content = metric_file.read_text(encoding='utf-8')
        assert "# 数据统计口径" in content

    def test_add_multiple_metrics(self, tmp_path):
        """Multiple metrics should be appended."""
        from scripts.metrics_manager import add_metric

        metric_file = tmp_path / "multi.md"
        add_metric("Metric 1", "Desc 1", str(metric_file))
        add_metric("Metric 2", "Desc 2", str(metric_file))

        content = metric_file.read_text(encoding='utf-8')
        assert "Metric 1" in content
        assert "Metric 2" in content
        assert "Desc 1" in content
        assert "Desc 2" in content
