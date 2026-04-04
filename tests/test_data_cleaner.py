import pytest
import os
import sys
import sqlite3
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.data_cleaner import clean_old_data


def test_clean_with_valid_tables(temp_db):
    """Clean with valid table names should succeed."""
    # Add metadata entry with old date
    conn = sqlite3.connect(temp_db)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS _data_skill_meta (
            table_name TEXT PRIMARY KEY,
            file_name TEXT,
            md5_hash TEXT,
            import_time DATETIME,
            last_used_time DATETIME
        )
    ''')
    conn.execute('''
        INSERT INTO _data_skill_meta (table_name, file_name, import_time, last_used_time)
        VALUES ('test_data', 'test.csv', '2020-01-01', '2020-01-01')
    ''')
    conn.commit()
    conn.close()

    clean_old_data(temp_db, days=30)
    # Should complete without error


def test_clean_blocks_sql_injection(temp_db, capsys):
    """SQL injection in table name from metadata should be skipped gracefully."""
    conn = sqlite3.connect(temp_db)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS _data_skill_meta (
            table_name TEXT PRIMARY KEY,
            file_name TEXT,
            md5_hash TEXT,
            import_time DATETIME,
            last_used_time DATETIME
        )
    ''')
    # Insert malicious table name
    conn.execute('''
        INSERT INTO _data_skill_meta (table_name, file_name, import_time, last_used_time)
        VALUES ('test; DROP TABLE test_data;--', 'test.csv', '2020-01-01', '2020-01-01')
    ''')
    conn.commit()
    conn.close()

    # Should complete without error (malicious table name is skipped)
    clean_old_data(temp_db, days=30)

    # Verify the test_data table still exists (wasn't dropped by injection)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_data'")
    assert cursor.fetchone() is not None, "test_data table should still exist (injection blocked)"
    conn.close()

    # Verify output shows the skip
    captured = capsys.readouterr()
    assert "跳过无效表名" in captured.out
