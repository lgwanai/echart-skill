import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.data_exporter import export_data


def test_export_with_valid_table(temp_db, temp_output_dir):
    """Export with valid table name should succeed."""
    output_path = os.path.join(temp_output_dir, "output.csv")
    export_data(temp_db, output_path, table_name="test_data")
    assert os.path.exists(output_path)


def test_export_with_sql_injection_blocked(temp_db, temp_output_dir):
    """SQL injection in table name should be blocked."""
    output_path = os.path.join(temp_output_dir, "output.csv")
    with pytest.raises(ValueError, match="无效的表名"):
        export_data(temp_db, output_path, table_name="test_data; DROP TABLE test_data;--")


def test_export_with_query(temp_db, temp_output_dir):
    """Export with query should succeed."""
    output_path = os.path.join(temp_output_dir, "output.csv")
    export_data(temp_db, output_path, query="SELECT name, value FROM test_data")
    assert os.path.exists(output_path)
