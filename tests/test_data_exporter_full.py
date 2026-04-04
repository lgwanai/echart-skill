import pytest
import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.data_exporter import export_data


class TestExporterFull:
    """Full coverage tests for data_exporter."""

    def test_export_to_excel(self, tmp_path):
        """Export to Excel format should work."""
        # Create test database
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE data (name TEXT, value INTEGER)")
        conn.execute("INSERT INTO data VALUES ('test', 1)")
        conn.commit()
        conn.close()

        # Export to Excel
        output_path = tmp_path / "output.xlsx"
        export_data(str(db_path), str(output_path), table_name="data")

        assert output_path.exists()

    def test_export_unsupported_format(self, tmp_path):
        """Unsupported format should raise error."""
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE data (name TEXT)")
        conn.commit()
        conn.close()

        output_path = tmp_path / "output.json"

        with pytest.raises(ValueError, match="Unsupported output format"):
            export_data(str(db_path), str(output_path), table_name="data")

    def test_export_missing_db(self, tmp_path):
        """Missing database should raise error."""
        output_path = tmp_path / "out.csv"

        with pytest.raises(FileNotFoundError):
            export_data("/nonexistent.db", str(output_path), table_name="data")

    def test_export_with_query(self, tmp_path):
        """Export with custom query should work."""
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE items (name TEXT, qty INTEGER)")
        conn.execute("INSERT INTO items VALUES ('a', 10)")
        conn.execute("INSERT INTO items VALUES ('b', 20)")
        conn.commit()
        conn.close()

        output_path = tmp_path / "filtered.csv"
        export_data(str(db_path), str(output_path), query="SELECT name FROM items WHERE qty > 15")

        assert output_path.exists()
        import pandas as pd
        df = pd.read_csv(output_path)
        assert len(df) == 1
        assert df.iloc[0]['name'] == 'b'

    def test_export_neither_table_nor_query(self, tmp_path):
        """Export without table_name or query should raise error."""
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE data (name TEXT)")
        conn.commit()
        conn.close()

        output_path = tmp_path / "out.csv"

        with pytest.raises(ValueError, match="Either table_name or query must be provided"):
            export_data(str(db_path), str(output_path))
