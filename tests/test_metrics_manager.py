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

    def test_main_function(self, tmp_path, monkeypatch, capsys):
        """main function should work with CLI args."""
        from scripts.metrics_manager import main

        metric_file = tmp_path / "cli_metrics.md"

        # Mock sys.argv
        monkeypatch.setattr(sys, 'argv', [
            'metrics_manager.py',
            '--name', 'CLI Metric',
            '--desc', 'CLI Description',
            '--file', str(metric_file)
        ])

        main()

        captured = capsys.readouterr()
        assert "成功追加统计口径" in captured.out
        assert metric_file.exists()

    def test_project_metric_only_effective_under_recorded_project(self, tmp_path, monkeypatch):
        """Project-level scope should be active only inside its project dir."""
        import scripts.metrics_manager as mm

        global_file = tmp_path / "global_metrics.md"
        index_file = tmp_path / "project_index.json"
        project_dir = tmp_path / "project"
        other_dir = tmp_path / "other"
        project_dir.mkdir()
        other_dir.mkdir()

        monkeypatch.setattr(mm, "GLOBAL_METRICS_PATH", global_file)
        monkeypatch.setattr(mm, "PROJECT_INDEX_PATH", index_file)

        mm.set_metric("全局GMV", "全局 GMV = SUM(amount)", level="global")
        mm.set_metric("项目GMV", "项目 GMV = SUM(project_amount)", level="project", project_dir=str(project_dir))

        active_inside = mm.render_effective_metrics(project_dir / "subdir")
        assert "全局GMV" in active_inside
        assert "项目GMV" in active_inside

        active_outside = mm.render_effective_metrics(other_dir)
        assert "全局GMV" in active_outside
        assert "项目GMV" not in active_outside

        index = index_file.read_text(encoding="utf-8")
        assert str(project_dir.resolve()) in index

    def test_metrics_cli_set_project(self, tmp_path, monkeypatch, capsys):
        """CLI set --level project should record project directory."""
        import scripts.metrics_manager as mm
        from scripts.metrics_manager import main

        index_file = tmp_path / "project_index.json"
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        monkeypatch.setattr(mm, "PROJECT_INDEX_PATH", index_file)
        monkeypatch.setattr(sys, 'argv', [
            'metrics_manager.py',
            'set',
            '--level', 'project',
            '--name', '项目订单数',
            '--desc', 'COUNT(DISTINCT order_id)',
            '--project-dir', str(project_dir),
        ])

        main()

        captured = capsys.readouterr()
        assert "成功设置项目统计口径" in captured.out
        assert (project_dir / ".echart-skill" / "metrics.md").exists()
