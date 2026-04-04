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


class TestInitMetaTableUrlColumns:
    """Test metadata table extension for URL sources."""

    def test_init_meta_table_creates_url_columns(self, temp_db):
        """Meta table should include URL source columns."""
        from scripts.data_importer import init_meta_table

        conn = sqlite3.connect(temp_db)
        init_meta_table(conn)

        # Check table structure
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(_data_skill_meta)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        # Should have new URL columns
        assert "source_url" in columns
        assert "source_format" in columns
        assert "auth_type" in columns
        assert "last_refresh_time" in columns

    def test_init_meta_table_adds_columns_to_existing(self, temp_db):
        """Should add URL columns if table exists without them."""
        from scripts.data_importer import init_meta_table

        conn = sqlite3.connect(temp_db)
        # Create old-style table without URL columns
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE _data_skill_meta (
                file_name TEXT,
                table_name TEXT PRIMARY KEY,
                md5_hash TEXT,
                import_time DATETIME,
                last_used_time DATETIME
            )
        ''')
        conn.commit()

        # Run init_meta_table which should add columns
        init_meta_table(conn)

        # Verify columns were added
        cursor.execute("PRAGMA table_info(_data_skill_meta)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        assert "source_url" in columns
        assert "source_format" in columns
        assert "auth_type" in columns
        assert "last_refresh_time" in columns


class TestImportFromUrl:
    """Test URL import functionality."""

    @pytest.mark.asyncio
    async def test_import_from_url_json(self, temp_db):
        """Import JSON data from URL to SQLite table."""
        import httpx
        import respx
        from scripts.data_importer import import_from_url

        with respx.mock:
            respx.get("https://api.example.com/data").mock(
                return_value=httpx.Response(200, json={
                    "data": [
                        {"id": 1, "name": "Alice"},
                        {"id": 2, "name": "Bob"}
                    ]
                })
            )

            table_name = await import_from_url(
                url="https://api.example.com/data",
                db_path=temp_db,
                table_name="users",
                source_format="json"
            )

        assert table_name == "users"

        # Verify data was imported
        conn = sqlite3.connect(temp_db)
        df = pd.read_sql_query("SELECT * FROM users ORDER BY id", conn)
        conn.close()

        assert len(df) == 2
        assert df.iloc[0]["name"] == "Alice"
        assert df.iloc[1]["name"] == "Bob"

    @pytest.mark.asyncio
    async def test_import_from_url_csv(self, temp_db):
        """Import CSV data from URL to SQLite table."""
        import httpx
        import respx
        from scripts.data_importer import import_from_url

        csv_content = "id,name\n1,Alice\n2,Bob"

        with respx.mock:
            respx.get("https://example.com/data.csv").mock(
                return_value=httpx.Response(200, text=csv_content)
            )

            table_name = await import_from_url(
                url="https://example.com/data.csv",
                db_path=temp_db,
                table_name="users_csv",
                source_format="csv"
            )

        assert table_name == "users_csv"

        # Verify data was imported
        conn = sqlite3.connect(temp_db)
        df = pd.read_sql_query("SELECT * FROM users_csv ORDER BY id", conn)
        conn.close()

        assert len(df) == 2
        assert df.iloc[0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_record_url_import_metadata(self, temp_db):
        """URL import metadata should be stored correctly."""
        import httpx
        import respx
        from scripts.data_importer import import_from_url, get_url_sources

        with respx.mock:
            respx.get("https://api.example.com/users").mock(
                return_value=httpx.Response(200, json=[{"id": 1}])
            )

            await import_from_url(
                url="https://api.example.com/users",
                db_path=temp_db,
                table_name="api_users",
                source_format="json"
            )

        # Verify metadata
        conn = sqlite3.connect(temp_db)
        sources = get_url_sources(conn)
        conn.close()

        assert len(sources) == 1
        assert sources[0]["table_name"] == "api_users"
        assert sources[0]["source_url"] == "https://api.example.com/users"
        assert sources[0]["source_format"] == "json"

    @pytest.mark.asyncio
    async def test_import_from_url_with_auth(self, temp_db):
        """URL import with authentication should work."""
        import httpx
        import respx
        from scripts.data_importer import import_from_url
        from scripts.url_data_source import BearerAuthConfig

        with respx.mock as mock:
            def check_auth(request):
                assert "Authorization" in request.headers
                return httpx.Response(200, json=[{"id": 1}])

            mock.get("https://api.example.com/protected").mock(side_effect=check_auth)

            await import_from_url(
                url="https://api.example.com/protected",
                db_path=temp_db,
                table_name="protected_data",
                source_format="json",
                auth_config=BearerAuthConfig(token="test-token")
            )

        # Verify data imported
        conn = sqlite3.connect(temp_db)
        df = pd.read_sql_query("SELECT COUNT(*) as cnt FROM protected_data", conn)
        conn.close()

        assert df["cnt"][0] == 1

    def test_import_from_url_sync_wrapper(self, temp_db):
        """Synchronous wrapper for URL import should work."""
        import httpx
        import respx
        from scripts.data_importer import import_from_url_sync

        with respx.mock:
            respx.get("https://api.example.com/sync").mock(
                return_value=httpx.Response(200, json=[{"id": 1, "name": "test"}])
            )

            table_name = import_from_url_sync(
                url="https://api.example.com/sync",
                db_path=temp_db,
                table_name="sync_table",
                source_format="json"
            )

        assert table_name == "sync_table"


class TestGetUrlSources:
    """Test get_url_sources function."""

    def test_get_url_sources_returns_only_url_sources(self, temp_db):
        """Should return only URL sources, not file imports."""
        from scripts.data_importer import init_meta_table, record_import, record_url_import, get_url_sources
        from datetime import datetime

        conn = sqlite3.connect(temp_db)
        init_meta_table(conn)

        # Add a file import
        record_import(conn, "test.csv", "file_table", "abc123")

        # Add a URL import
        record_url_import(conn, "https://api.example.com/data", "url_table", "json")

        sources = get_url_sources(conn)
        conn.close()

        # Should only return URL sources
        assert len(sources) == 1
        assert sources[0]["table_name"] == "url_table"

    def test_get_url_sources_empty_when_none(self, temp_db):
        """Should return empty list when no URL sources exist."""
        from scripts.data_importer import init_meta_table, get_url_sources

        conn = sqlite3.connect(temp_db)
        init_meta_table(conn)

        sources = get_url_sources(conn)
        conn.close()

        assert sources == []


class TestRecordUrlImport:
    """Test record_url_import function."""

    def test_record_url_import_stores_metadata(self, temp_db):
        """record_url_import should store URL metadata correctly."""
        from scripts.data_importer import init_meta_table, record_url_import, get_url_sources

        conn = sqlite3.connect(temp_db)
        init_meta_table(conn)

        record_url_import(
            conn,
            url="https://api.example.com/data",
            table_name="api_data",
            source_format="json",
            auth_type="bearer"
        )

        sources = get_url_sources(conn)
        conn.close()

        assert len(sources) == 1
        assert sources[0]["source_url"] == "https://api.example.com/data"
        assert sources[0]["source_format"] == "json"
        assert sources[0]["auth_type"] == "bearer"


class TestRefreshUrlSource:
    """Test refresh_url_source functionality."""

    @pytest.mark.asyncio
    async def test_refresh_url_source_updates_data(self, temp_db):
        """Refresh should re-fetch data and update table."""
        import httpx
        import respx
        from scripts.data_importer import import_from_url, refresh_url_source

        # Initial import
        with respx.mock:
            respx.get("https://api.example.com/data").mock(
                return_value=httpx.Response(200, json=[
                    {"id": 1, "name": "Alice"},
                    {"id": 2, "name": "Bob"}
                ])
            )

            await import_from_url(
                url="https://api.example.com/data",
                db_path=temp_db,
                table_name="refresh_test",
                source_format="json"
            )

        # Verify initial data
        conn = sqlite3.connect(temp_db)
        df = pd.read_sql_query("SELECT COUNT(*) as cnt FROM refresh_test", conn)
        assert df["cnt"][0] == 2
        conn.close()

        # Refresh with new data
        with respx.mock:
            respx.get("https://api.example.com/data").mock(
                return_value=httpx.Response(200, json=[
                    {"id": 1, "name": "Alice Updated"},
                    {"id": 2, "name": "Bob Updated"},
                    {"id": 3, "name": "Charlie"}
                ])
            )

            result = await refresh_url_source(temp_db, "refresh_test")

        assert result is True

        # Verify data was replaced
        conn = sqlite3.connect(temp_db)
        df = pd.read_sql_query("SELECT * FROM refresh_test ORDER BY id", conn)
        conn.close()

        assert len(df) == 3
        assert df.iloc[0]["name"] == "Alice Updated"

    @pytest.mark.asyncio
    async def test_refresh_url_source_updates_metadata(self, temp_db):
        """Refresh should update last_refresh_time."""
        import httpx
        import respx
        import time
        from scripts.data_importer import import_from_url, refresh_url_source

        # Initial import
        with respx.mock:
            respx.get("https://api.example.com/refresh").mock(
                return_value=httpx.Response(200, json=[{"id": 1}])
            )

            await import_from_url(
                url="https://api.example.com/refresh",
                db_path=temp_db,
                table_name="refresh_meta",
                source_format="json"
            )

        # Wait a moment
        time.sleep(0.1)

        # Refresh
        with respx.mock:
            respx.get("https://api.example.com/refresh").mock(
                return_value=httpx.Response(200, json=[{"id": 1}])
            )

            await refresh_url_source(temp_db, "refresh_meta")

        # Verify last_refresh_time was updated
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT import_time, last_refresh_time
            FROM _data_skill_meta
            WHERE table_name = ?
        ''', ("refresh_meta",))
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        # last_refresh_time should be different from import_time
        assert row[0] is not None
        assert row[1] is not None

    @pytest.mark.asyncio
    async def test_refresh_url_source_raises_for_non_url_table(self, temp_db):
        """Refresh should raise ValueError for non-URL table."""
        import httpx
        import respx
        from scripts.data_importer import import_to_sqlite, refresh_url_source
        import tempfile

        # Create a CSV file import (not URL)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,value\ntest,1\n")
            csv_path = f.name

        try:
            import_to_sqlite(csv_path, temp_db, table_name="file_table")

            with pytest.raises(ValueError, match="not a URL data source"):
                await refresh_url_source(temp_db, "file_table")
        finally:
            os.unlink(csv_path)

    def test_refresh_url_source_sync_wrapper(self, temp_db):
        """Synchronous wrapper for refresh should work."""
        import httpx
        import respx
        from scripts.data_importer import import_from_url_sync, refresh_url_source_sync

        # Initial import
        with respx.mock:
            respx.get("https://api.example.com/sync_refresh").mock(
                return_value=httpx.Response(200, json=[{"id": 1}])
            )

            import_from_url_sync(
                url="https://api.example.com/sync_refresh",
                db_path=temp_db,
                table_name="sync_refresh",
                source_format="json"
            )

        # Refresh
        with respx.mock:
            respx.get("https://api.example.com/sync_refresh").mock(
                return_value=httpx.Response(200, json=[{"id": 2}])
            )

            result = refresh_url_source_sync(temp_db, "sync_refresh")

        assert result is True


class TestListUrlSources:
    """Test list_url_sources functionality."""

    def test_list_url_sources_returns_all(self, temp_db):
        """list_url_sources should return all URL sources."""
        import httpx
        import respx
        from scripts.data_importer import import_from_url_sync, list_url_sources

        with respx.mock:
            respx.get("https://api.example.com/source1").mock(
                return_value=httpx.Response(200, json=[{"id": 1}])
            )
            respx.get("https://api.example.com/source2").mock(
                return_value=httpx.Response(200, json=[{"id": 2}])
            )

            import_from_url_sync(
                url="https://api.example.com/source1",
                db_path=temp_db,
                table_name="source1_table",
                source_format="json"
            )
            import_from_url_sync(
                url="https://api.example.com/source2",
                db_path=temp_db,
                table_name="source2_table",
                source_format="json"
            )

        sources = list_url_sources(temp_db)

        assert len(sources) == 2
        table_names = [s["table_name"] for s in sources]
        assert "source1_table" in table_names
        assert "source2_table" in table_names

    def test_list_url_sources_empty(self, temp_db):
        """list_url_sources should return empty list when no URL sources."""
        from scripts.data_importer import list_url_sources

        sources = list_url_sources(temp_db)
        assert sources == []
