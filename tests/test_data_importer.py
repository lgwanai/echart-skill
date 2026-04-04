import pytest
import os
import sys
import sqlite3
import pandas as pd
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.data_importer import (
    import_to_sqlite,
    clean_column_names,
    find_header_row,
    calculate_md5,
    check_duplicate_import,
    init_meta_table,
)


class TestCleanColumnNames:
    """Test column name cleaning."""

    def test_normal_names(self):
        """Normal names should pass through."""
        result = clean_column_names(["name", "age", "value"])
        assert result == ["name", "age", "value"]

    def test_special_characters(self):
        """Special characters should be replaced with underscore."""
        result = clean_column_names(["user name", "age-value", "data.file"])
        assert "_" in result[0]
        assert "_" in result[1]
        assert "_" in result[2]

    def test_leading_numbers(self):
        """Columns that are entirely numbers should be prefixed with col_."""
        # "456" is entirely digits, so it gets prefixed
        result = clean_column_names(["123col", "456"])
        # "123col" contains letters after digits, so underscores replace non-alphanumeric
        assert "_" in result[0] or result[0] == "123col"
        # "456" is all digits, gets col_ prefix
        assert result[1].startswith("col_")

    def test_chinese_characters(self):
        """Chinese characters should be handled."""
        result = clean_column_names(["姓名", "年龄"])
        # Should convert to something valid
        assert all(c.isidentifier() or "_" in c for c in result)

    def test_duplicate_names(self):
        """Duplicate names should be made unique."""
        result = clean_column_names(["name", "name", "name"])
        assert len(set(result)) == 3

    def test_empty_column(self):
        """Empty columns should get default name."""
        result = clean_column_names(["", "valid", None])
        assert result[0] != ""
        assert result[2] != ""


class TestFindHeaderRow:
    """Test header row detection."""

    def test_header_at_top(self):
        """Header at row 0 should be detected."""
        df = pd.DataFrame({
            "name": ["Alice", "Bob"],
            "age": [25, 30]
        })
        assert find_header_row(df) == 0

    def test_header_after_empty_rows(self):
        """Header after empty rows should be detected."""
        df = pd.DataFrame({
            0: [None, None, "name", "Alice"],
            1: [None, None, "age", "25"]
        })
        result = find_header_row(df)
        assert result == 2


class TestCalculateMD5:
    """Test MD5 calculation."""

    def test_md5_consistency(self, tmp_path):
        """Same content should produce same MD5."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("test,content\n1,2\n")

        md5_1 = calculate_md5(str(test_file))
        md5_2 = calculate_md5(str(test_file))
        assert md5_1 == md5_2
        assert len(md5_1) == 32  # MD5 hex length

    def test_different_content_different_md5(self, tmp_path):
        """Different content should produce different MD5."""
        file1 = tmp_path / "file1.csv"
        file2 = tmp_path / "file2.csv"
        file1.write_text("content1")
        file2.write_text("content2")

        assert calculate_md5(str(file1)) != calculate_md5(str(file2))


class TestImportToSQLite:
    """Test file import functionality."""

    def test_csv_import(self, temp_db, tmp_path):
        """CSV file should be imported correctly."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age\nAlice,25\nBob,30\n")

        tables = import_to_sqlite(str(csv_file), temp_db)
        assert len(tables) == 1

        # Verify data
        conn = sqlite3.connect(temp_db)
        df = pd.read_sql_query("SELECT * FROM test", conn)
        conn.close()

        assert len(df) == 2
        assert "name" in df.columns
        assert "age" in df.columns

    def test_excel_import(self, temp_db, tmp_path):
        """Excel file should be imported correctly."""
        # Create test Excel file
        df = pd.DataFrame({"name": ["Alice", "Bob"], "value": [100, 200]})
        excel_file = tmp_path / "test.xlsx"
        df.to_excel(str(excel_file), index=False)

        tables = import_to_sqlite(str(excel_file), temp_db)
        assert len(tables) == 1

        # Verify data
        conn = sqlite3.connect(temp_db)
        result = pd.read_sql_query("SELECT COUNT(*) as cnt FROM test", conn)
        conn.close()

        assert result["cnt"][0] == 2

    def test_duplicate_detection(self, temp_db, tmp_path):
        """Duplicate file should not be re-imported."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age\nAlice,25\n")

        # First import
        tables1 = import_to_sqlite(str(csv_file), temp_db)
        assert len(tables1) == 1

        # Second import (same file)
        tables2 = import_to_sqlite(str(csv_file), temp_db)
        assert len(tables2) == 1  # Returns existing table

    def test_nonexistent_file(self, temp_db):
        """Nonexistent file should raise error."""
        with pytest.raises(FileNotFoundError):
            import_to_sqlite("/nonexistent/file.csv", temp_db)


class TestInitMetaTable:
    """Test metadata table initialization."""

    def test_meta_table_creation(self, temp_db):
        """Meta table should be created correctly."""
        conn = sqlite3.connect(temp_db)
        init_meta_table(conn)

        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_data_skill_meta'")
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "_data_skill_meta"


class TestCheckDuplicateImport:
    """Test duplicate import detection."""

    def test_no_duplicate(self, temp_db):
        """Should return None for new file."""
        conn = sqlite3.connect(temp_db)
        init_meta_table(conn)

        result = check_duplicate_import(conn, "new_md5_hash")
        conn.close()

        assert result is None

    def test_duplicate_found(self, temp_db):
        """Should return table names for duplicate file."""
        import hashlib
        from datetime import datetime

        conn = sqlite3.connect(temp_db)
        init_meta_table(conn)

        # Insert a record manually
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO _data_skill_meta
            (file_name, table_name, md5_hash, import_time, last_used_time)
            VALUES (?, ?, ?, ?, ?)
        ''', ("test.csv", "test_table", "known_md5_hash", now, now))
        conn.commit()

        result = check_duplicate_import(conn, "known_md5_hash")
        conn.close()

        assert result is not None
        assert "test_table" in result
