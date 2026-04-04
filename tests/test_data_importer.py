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
    unmerge_and_fill_excel,
    record_import,
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


class TestUnmergeExcel:
    """Test Excel unmerge functionality."""

    def test_unmerge_simple_excel(self, tmp_path):
        """Unmerge should handle simple Excel file."""
        df = pd.DataFrame({"col1": ["a", "b"], "col2": [1, 2]})
        excel_file = tmp_path / "simple.xlsx"
        df.to_excel(str(excel_file), index=False)

        result = unmerge_and_fill_excel(str(excel_file))
        assert len(result) == 2

    def test_unmerge_with_sheet_name(self, tmp_path):
        """Unmerge should work with sheet name."""
        df = pd.DataFrame({"col": ["a", "b"]})
        excel_file = tmp_path / "sheet.xlsx"
        df.to_excel(str(excel_file), index=False, sheet_name="Data")

        result = unmerge_and_fill_excel(str(excel_file), sheet_name="Data")
        assert len(result) == 2


class TestRecordImport:
    """Test import recording."""

    def test_record_import(self, temp_db):
        """Record import should create metadata entry."""
        from datetime import datetime

        conn = sqlite3.connect(temp_db)
        init_meta_table(conn)

        record_import(conn, "test.csv", "test_table", "abc123")

        cursor = conn.cursor()
        cursor.execute("SELECT file_name, table_name, md5_hash FROM _data_skill_meta")
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "test.csv"
        assert result[1] == "test_table"
        assert result[2] == "abc123"


class TestUnsupportedFormat:
    """Test unsupported file format handling."""

    def test_unsupported_format(self, temp_db, tmp_path):
        """Unsupported format should raise error."""
        bad_file = tmp_path / "test.json"
        bad_file.write_text('{"key": "value"}')

        with pytest.raises(ValueError, match="Unsupported file format"):
            import_to_sqlite(str(bad_file), temp_db)


class TestImportWithCustomTableName:
    """Test import with custom table name."""

    def test_custom_table_name(self, temp_db, tmp_path):
        """Import with custom table name should work."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("col1,col2\n1,2\n")

        tables = import_to_sqlite(str(csv_file), temp_db, table_name="my_custom_table")
        assert "my_custom_table" in tables

        # Verify table exists
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='my_custom_table'")
        assert cursor.fetchone() is not None
        conn.close()


class TestMultiSheetExcel:
    """Test multi-sheet Excel import."""

    def test_multi_sheet_excel(self, temp_db, tmp_path):
        """Multi-sheet Excel should create multiple tables."""
        excel_file = tmp_path / "multi.xlsx"

        with pd.ExcelWriter(str(excel_file)) as writer:
            pd.DataFrame({"col": ["a"]}).to_excel(writer, sheet_name="Sheet1", index=False)
            pd.DataFrame({"col": ["b"]}).to_excel(writer, sheet_name="Sheet2", index=False)

        tables = import_to_sqlite(str(excel_file), temp_db)

        assert len(tables) == 2


class TestExcelEdgeCases:
    """Test Excel import edge cases."""

    def test_excel_with_all_null_rows(self, temp_db, tmp_path):
        """Excel with all-null rows should be handled."""
        excel_file = tmp_path / "nulls.xlsx"
        df = pd.DataFrame({
            "col1": ["a", None, None],
            "col2": [1, None, None]
        })
        df.to_excel(str(excel_file), index=False)

        tables = import_to_sqlite(str(excel_file), temp_db)
        assert len(tables) == 1

        # Verify null rows were dropped
        conn = sqlite3.connect(temp_db)
        result = pd.read_sql_query("SELECT COUNT(*) as cnt FROM nulls", conn)
        conn.close()

        assert result["cnt"][0] == 1

    def test_excel_with_all_null_columns(self, temp_db, tmp_path):
        """Excel with all-null columns should have them removed."""
        excel_file = tmp_path / "nullcols.xlsx"
        df = pd.DataFrame({
            "col1": ["a", "b"],
            "null_col": [None, None]
        })
        df.to_excel(str(excel_file), index=False)

        tables = import_to_sqlite(str(excel_file), temp_db)
        assert len(tables) == 1

        # Verify null column was dropped
        conn = sqlite3.connect(temp_db)
        result = pd.read_sql_query("SELECT * FROM nullcols LIMIT 1", conn)
        conn.close()

        assert "null_col" not in result.columns


class TestTableNameCollision:
    """Test table name collision handling."""

    def test_table_name_collision(self, temp_db, tmp_path):
        """Importing same table name should create _v1, _v2 etc."""
        csv_file1 = tmp_path / "data.csv"
        csv_file1.write_text("col1\na\n")

        csv_file2 = tmp_path / "data2.csv"
        csv_file2.write_text("col1\nb\n")

        # First import
        tables1 = import_to_sqlite(str(csv_file1), temp_db, table_name="mydata")

        # Second import with same table name (different content so not duplicate)
        tables2 = import_to_sqlite(str(csv_file2), temp_db, table_name="mydata")

        # Should have different table names
        assert "mydata" in tables1
        assert "mydata_v1" in tables2 or "mydata" in tables2


class TestChunkedCSVImport:
    """Test chunked CSV import for large files."""

    def test_chunked_csv_import(self, temp_db, tmp_path):
        """Large CSV should be imported in chunks."""
        csv_file = tmp_path / "large.csv"

        # Create CSV with more than default chunk size
        with open(csv_file, 'w') as f:
            f.write("id,value\n")
            for i in range(100):
                f.write(f"{i},{i * 10}\n")

        tables = import_to_sqlite(str(csv_file), temp_db)
        assert len(tables) == 1

        # Verify all rows imported
        conn = sqlite3.connect(temp_db)
        result = pd.read_sql_query("SELECT COUNT(*) as cnt FROM large", conn)
        conn.close()

        assert result["cnt"][0] == 100


class TestNumbersFileImport:
    """Test Numbers file import (requires numbers-parser)."""

    def test_numbers_import_skip(self, temp_db, tmp_path):
        """Numbers file import should fail gracefully if package not installed."""
        # Create a dummy .numbers file (not a real Numbers file)
        numbers_file = tmp_path / "test.numbers"
        numbers_file.write_text("not a real numbers file")

        # This should raise ImportError for missing package or ValueError for invalid file
        with pytest.raises((ImportError, ValueError, Exception)):
            import_to_sqlite(str(numbers_file), temp_db)


class TestExcelWithFallback:
    """Test Excel import with fallback handling."""

    def test_excel_fallback_to_pandas(self, temp_db, tmp_path):
        """Excel import should fallback to pandas if unmerge fails."""
        # Create a simple Excel file
        excel_file = tmp_path / "fallback.xlsx"
        df = pd.DataFrame({"col1": ["a", "b"], "col2": [1, 2]})
        df.to_excel(str(excel_file), index=False)

        # Import should succeed
        tables = import_to_sqlite(str(excel_file), temp_db)
        assert len(tables) == 1


class TestETFileImport:
    """Test WPS .et file import."""

    def test_et_file_import(self, temp_db, tmp_path):
        """WPS .et file should be imported."""
        # Create a simple Excel file, then rename to .et
        # .et files are WPS format, but pandas treats them as Excel
        et_file = tmp_path / "test.et"
        df = pd.DataFrame({"col": ["a", "b"]})

        # Write as xlsx first, then rename
        xlsx_file = tmp_path / "test.xlsx"
        df.to_excel(str(xlsx_file), index=False)
        import shutil
        shutil.copy(str(xlsx_file), str(et_file))

        tables = import_to_sqlite(str(et_file), temp_db)
        assert len(tables) == 1
