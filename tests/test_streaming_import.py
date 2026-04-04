"""Tests for streaming Excel import functionality.

This module tests the streaming import feature for large Excel files.
Per locked decision "始终使用流式导入", ALL Excel files must use streaming.
"""
import pytest
import os
import sys
import sqlite3
import tempfile
import pandas as pd
from unittest.mock import patch, MagicMock, call
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestStreamingAlwaysUsedForExcel:
    """Test that ALL Excel files use streaming import."""

    def test_streaming_always_used_for_excel(self, tmp_path):
        """Even small Excel files must use streaming per locked decision.

        This test verifies that streaming is ALWAYS used, regardless of file size.
        Per the locked decision "始终使用流式导入" (always use streaming).
        """
        from scripts.data_importer import import_to_sqlite

        # Create a small Excel file (even 1KB should trigger streaming)
        excel_file = tmp_path / "small.xlsx"
        df = pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "value": [100, 200, 300]
        })
        df.to_excel(str(excel_file), index=False)

        # Create temp database
        db_file = tmp_path / "test.db"

        # Mock import_excel_streaming to verify it's called
        with patch('scripts.data_importer.import_excel_streaming') as mock_streaming:
            # Setup mock to return row count
            mock_streaming.return_value = iter([3])  # 3 rows processed

            # Mock getsize to return a small file size
            with patch('os.path.getsize', return_value=1024):  # 1KB file
                try:
                    import_to_sqlite(str(excel_file), str(db_file))
                except Exception:
                    pass  # May fail due to mocking, that's OK

            # Verify streaming was called (proves ALL Excel files use streaming)
            mock_streaming.assert_called_once()


class TestStreamingReadsInChunks:
    """Test that streaming reads rows in chunks."""

    def test_streaming_reads_in_chunks(self, tmp_path):
        """Streaming import should read rows in chunks of 10,000."""
        from scripts.data_importer import import_excel_streaming

        # Create an Excel file with 25 rows
        excel_file = tmp_path / "test_chunks.xlsx"
        df = pd.DataFrame({
            "id": list(range(25)),
            "value": [f"val_{i}" for i in range(25)]
        })
        df.to_excel(str(excel_file), index=False)

        # Create temp database
        db_file = tmp_path / "test_chunks.db"
        conn = sqlite3.connect(str(db_file))

        # Temporarily set chunk size to 10 for testing via module patch
        import scripts.data_importer as importer_module
        original_chunk_size = importer_module.STREAMING_CHUNK_SIZE
        importer_module.STREAMING_CHUNK_SIZE = 10

        try:
            rows_processed = list(import_excel_streaming(
                str(excel_file), str(db_file), "test_table", conn
            ))

            # Verify 3 chunks were processed (25 rows / 10 per chunk = 3 chunks)
            # Note: Last chunk may have fewer rows
            assert len(rows_processed) >= 2  # At least 2 progress yields for 25 rows with chunk=10

            # Verify all rows were inserted
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_table")
            count = cursor.fetchone()[0]
            assert count == 25, f"Expected 25 rows, got {count}"
        finally:
            importer_module.STREAMING_CHUNK_SIZE = original_chunk_size
            conn.close()

    def test_chunk_size_constant_exists(self):
        """STREAMING_CHUNK_SIZE constant should be defined."""
        try:
            from scripts.data_importer import STREAMING_CHUNK_SIZE
            assert STREAMING_CHUNK_SIZE == 10000
        except ImportError:
            pytest.fail("STREAMING_CHUNK_SIZE not defined")


class TestStreamingInsertsAllRows:
    """Test that streaming correctly inserts all rows."""

    def test_streaming_inserts_all_rows(self, tmp_path):
        """All rows from Excel should be inserted into database."""
        from scripts.data_importer import import_excel_streaming

        # Create an Excel file with test data
        excel_file = tmp_path / "test_data.xlsx"
        df = pd.DataFrame({
            "category": ["A", "B", "C", "D", "E"],
            "amount": [100, 200, 300, 400, 500]
        })
        df.to_excel(str(excel_file), index=False)

        # Create temp database
        db_file = tmp_path / "test_data.db"
        conn = sqlite3.connect(str(db_file))

        try:
            # Run streaming import
            list(import_excel_streaming(
                str(excel_file), str(db_file), "sales_data", conn
            ))

            # Verify all rows were inserted
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sales_data")
            count = cursor.fetchone()[0]

            assert count == 5, f"Expected 5 rows, got {count}"

            # Verify data integrity
            cursor.execute("SELECT SUM(amount) FROM sales_data")
            total = cursor.fetchone()[0]
            assert total == 1500, f"Expected total 1500, got {total}"

        except Exception as e:
            pytest.fail(f"import_excel_streaming not implemented or failed: {e}")
        finally:
            conn.close()


class TestLargeFileSizeValidation:
    """Test file size validation for Excel files."""

    def test_large_file_size_validation(self, tmp_path):
        """Files > 100MB should raise ValueError with Chinese error message."""
        from scripts.data_importer import import_excel_streaming

        # Create a small Excel file for testing
        excel_file = tmp_path / "large.xlsx"
        df = pd.DataFrame({"col": ["data"]})
        df.to_excel(str(excel_file), index=False)

        db_file = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_file))

        # Mock getsize to return > 100MB - patch at module level
        import scripts.data_importer as importer_module
        large_size = 101 * 1024 * 1024  # 101MB

        original_getsize = importer_module.os.path.getsize
        importer_module.os.path.getsize = lambda x: large_size

        try:
            with pytest.raises(ValueError) as exc_info:
                list(import_excel_streaming(
                    str(excel_file), str(db_file), "test_table", conn
                ))

            # Verify Chinese error message
            error_msg = str(exc_info.value)
            assert "过大" in error_msg or "100MB" in error_msg, \
                f"Expected Chinese error message about file size, got: {error_msg}"
        finally:
            importer_module.os.path.getsize = original_getsize
            conn.close()

    def test_max_excel_size_constant_exists(self):
        """MAX_EXCEL_SIZE constant should be defined."""
        try:
            from scripts.data_importer import MAX_EXCEL_SIZE
            # 100MB in bytes
            expected = 100 * 1024 * 1024
            assert MAX_EXCEL_SIZE == expected, \
                f"Expected MAX_EXCEL_SIZE={expected}, got {MAX_EXCEL_SIZE}"
        except ImportError:
            pytest.fail("MAX_EXCEL_SIZE not defined")
