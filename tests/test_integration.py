import pytest
import os
import sys
import sqlite3
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Mock the server module before importing chart_generator
import unittest.mock as mock
sys.modules['server'] = mock.MagicMock()
sys.modules['server'].ensure_server_running = mock.MagicMock(return_value='http://localhost:8080')

from scripts.data_importer import import_to_sqlite
from scripts.data_exporter import export_data
from scripts.chart_generator import generate_chart
from scripts.data_cleaner import clean_old_data


class TestImportExportWorkflow:
    """End-to-end import and export tests."""

    def test_csv_import_export_roundtrip(self, tmp_path):
        """Data should be preserved through import -> export cycle."""
        # Create source CSV
        source_csv = tmp_path / "source.csv"
        source_data = "name,age,city\nAlice,25,Beijing\nBob,30,Shanghai\n"
        source_csv.write_text(source_data, encoding='utf-8')

        # Create temp database
        db_path = tmp_path / "test.db"

        # Import
        tables = import_to_sqlite(str(source_csv), str(db_path))
        assert len(tables) == 1
        table_name = tables[0]

        # Export to new CSV
        export_csv = tmp_path / "export.csv"
        export_data(str(db_path), str(export_csv), table_name=table_name)

        # Verify data integrity
        original_df = pd.read_csv(source_csv)
        exported_df = pd.read_csv(export_csv)

        assert len(original_df) == len(exported_df)
        assert list(original_df.columns) == list(exported_df.columns)

    def test_excel_import_chart_export(self, tmp_path):
        """Excel data should flow through to chart generation."""
        # Create Excel file
        excel_file = tmp_path / "sales.xlsx"
        df = pd.DataFrame({
            "category": ["A", "B", "C"],
            "sales": [100, 200, 150]
        })
        df.to_excel(str(excel_file), index=False)

        # Create temp database
        db_path = tmp_path / "chart.db"

        # Import
        tables = import_to_sqlite(str(excel_file), str(db_path))
        assert len(tables) == 1

        # Generate chart
        chart_config = {
            "db_path": str(db_path),
            "query": "SELECT category, sales FROM sales",
            "title": "Sales Chart",
            "output_path": str(tmp_path / "chart.html"),
            "echarts_option": {
                "xAxis": {"type": "category"},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar", "encode": {"x": "category", "y": "sales"}}]
            }
        }
        with mock.patch('scripts.chart_generator.get_baidu_ak', return_value=None):
            result = generate_chart(chart_config)

        # Verify chart was created
        assert result is not None
        assert os.path.exists(result)

        # Verify HTML content
        with open(result, 'r', encoding='utf-8') as f:
            html = f.read()
        assert "echarts" in html.lower()
        assert "Sales Chart" in html


class TestMetadataWorkflow:
    """Test metadata tracking through workflows."""

    def test_import_creates_metadata(self, tmp_path):
        """Import should create metadata entries."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("col1,col2\n1,2\n")
        db_path = tmp_path / "meta.db"

        import_to_sqlite(str(csv_file), str(db_path))

        # Check metadata table
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_data_skill_meta'")
        assert cursor.fetchone() is not None

        cursor.execute("SELECT COUNT(*) FROM _data_skill_meta")
        count = cursor.fetchone()[0]
        conn.close()

        assert count > 0

    def test_duplicate_import_updates_timestamp(self, tmp_path):
        """Re-importing same file should update last_used_time."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("col1,col2\n1,2\n")
        db_path = tmp_path / "dup.db"

        # First import
        import_to_sqlite(str(csv_file), str(db_path))

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT last_used_time FROM _data_skill_meta")
        time1 = cursor.fetchone()[0]

        # Small delay to ensure different timestamp
        import time
        time.sleep(1)

        # Second import (same file)
        import_to_sqlite(str(csv_file), str(db_path))

        cursor.execute("SELECT last_used_time FROM _data_skill_meta")
        time2 = cursor.fetchone()[0]
        conn.close()

        # Timestamp should be updated
        assert time2 >= time1


class TestCleanupWorkflow:
    """Test data cleanup integration."""

    def test_cleanup_removes_old_data(self, tmp_path):
        """Clean old data should remove stale tables."""
        csv_file = tmp_path / "old_data.csv"
        csv_file.write_text("col1,col2\n1,2\n")
        db_path = tmp_path / "clean.db"

        # Import data
        import_to_sqlite(str(csv_file), str(db_path))

        # Manually set old timestamp
        conn = sqlite3.connect(str(db_path))
        conn.execute('''
            UPDATE _data_skill_meta
            SET last_used_time = '2000-01-01 00:00:00'
        ''')
        conn.commit()
        conn.close()

        # Run cleanup
        clean_old_data(str(db_path), days=30)

        # Verify table was removed
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='old_data'")
        result = cursor.fetchone()
        conn.close()

        assert result is None


class TestSecurityIntegration:
    """Test security features in integrated workflows."""

    def test_sql_injection_blocked_in_export(self, tmp_path):
        """SQL injection should be blocked in export."""
        csv_file = tmp_path / "safe.csv"
        csv_file.write_text("name,value\ntest,1\n")
        db_path = tmp_path / "sec.db"

        import_to_sqlite(str(csv_file), str(db_path))

        export_path = tmp_path / "output.csv"

        # Try SQL injection through table name
        with pytest.raises(ValueError, match="无效的表名"):
            export_data(str(db_path), str(export_path), table_name="safe; DROP TABLE safe;--")

    def test_path_traversal_blocked_in_server(self, tmp_path):
        """Path traversal should be blocked by validators."""
        from validators import validate_file_path

        with pytest.raises(ValueError, match="不在允许的目录"):
            validate_file_path("/etc/passwd", str(tmp_path))

        with pytest.raises(ValueError, match="不在允许的目录"):
            validate_file_path(str(tmp_path / ".." / ".." / "etc" / "passwd"), str(tmp_path))
