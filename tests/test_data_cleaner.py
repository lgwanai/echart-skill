import pytest
import os
import sys
import duckdb
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.data_cleaner import clean_old_data, clean_table_data


def test_clean_with_valid_tables(temp_db):
    """Clean with valid table names should succeed."""
    # Add metadata entry with old date
    conn = duckdb.connect(temp_db)
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


def test_clean_blocks_sql_injection(temp_db, caplog):
    """SQL injection in table name from metadata should be skipped gracefully."""
    import logging
    caplog.set_level(logging.WARNING)

    conn = duckdb.connect(temp_db)
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
    conn = duckdb.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name='test_data'")
    assert cursor.fetchone() is not None, "test_data table should still exist (injection blocked)"
    conn.close()

    # Verify output shows the skip in logs
    assert any("跳过无效表名" in record.message for record in caplog.records)


def test_clean_table_converts_types_and_deduplicates(tmp_path):
    """Content cleaning should convert dates/money and dedupe by multiple keys."""
    db_path = tmp_path / "clean_content.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute("""
        CREATE TABLE orders_raw (
            order_id TEXT,
            line_id TEXT,
            order_date TEXT,
            amount TEXT,
            updated_at TEXT,
            province TEXT
        )
    """)
    conn.execute("""
        INSERT INTO orders_raw VALUES
        ('o1', 'l1', '2026/06/01', '¥1,234.567', '2026-06-01 10:00:00', ' 广东省 '),
        ('o1', 'l1', '2026/06/01', '¥1,236.555', '2026-06-01 11:00:00', '广东省'),
        ('o2', 'l1', 'bad-date', '88.8', '2026-06-02 09:00:00', '浙江省')
    """)
    conn.close()

    report = clean_table_data(
        str(db_path),
        "orders_raw",
        config={
            "output_table": "orders_cleaned",
            "unique_key": ["order_id", "line_id"],
            "duplicate_keep": "latest",
            "duplicate_order_by": "updated_at",
            "type_conversions": [
                {"column": "order_date", "type": "date"},
                {"column": "amount", "type": "money", "decimals": 2},
            ],
            "text_cleaning": [
                {"column": "province", "strip": True, "replace": {"省": ""}},
            ],
        },
    )

    import database
    database._cleanup_repo()

    conn = duckdb.connect(str(db_path))
    rows = conn.execute("SELECT order_id, line_id, order_date, amount, province FROM orders_cleaned ORDER BY order_id").fetchall()
    type_row = conn.execute("SELECT TYPEOF(order_date), TYPEOF(amount) FROM orders_cleaned LIMIT 1").fetchone()
    conn.close()

    assert report["deduplication"]["removed_rows"] == 1
    assert len(rows) == 2
    assert rows[0][3] == pytest.approx(1236.56)
    assert rows[0][4] == "广东"
    assert type_row[0] == "DATE"


def test_clean_table_rules_and_cross_table_validation(tmp_path):
    """Rule engine and cross-table validation should report violations."""
    db_path = tmp_path / "clean_rules.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute("""
        CREATE TABLE users_raw (
            user_id TEXT,
            register_date DATE,
            first_purchase_date DATE,
            age INTEGER,
            phone TEXT
        )
    """)
    conn.execute("""
        INSERT INTO users_raw VALUES
        ('u1', '2026-01-01', '2026-01-03', 30, '13812345678'),
        ('u2', '2026-02-10', '2026-02-01', 200, '13912345678')
    """)
    conn.execute("CREATE TABLE first_purchases (user_id TEXT, first_purchase_date DATE)")
    conn.execute("""
        INSERT INTO first_purchases VALUES
        ('u1', '2026-01-03'),
        ('u2', '2026-02-01')
    """)
    conn.close()

    report = clean_table_data(
        str(db_path),
        "users_raw",
        config={
            "output_table": "users_cleaned",
            "unique_key": "user_id",
            "outliers": [
                {"column": "age", "method": "bounds", "min": 0, "max": 150, "action": "null"}
            ],
            "rules": [
                {"name": "register_before_purchase", "left": "register_date", "op": "<=", "right": "first_purchase_date"}
            ],
            "cross_table_rules": [
                {
                    "name": "cross_register_before_purchase",
                    "table": "first_purchases",
                    "key": ["user_id"],
                    "left": "register_date",
                    "op": "<=",
                    "right": "first_purchase_date",
                }
            ],
            "masking": [
                {"column": "phone", "method": "middle", "keep_start": 3, "keep_end": 4}
            ],
        },
    )

    import database
    database._cleanup_repo()

    conn = duckdb.connect(str(db_path))
    rows = conn.execute("SELECT user_id, age, register_before_purchase_violation, phone FROM users_cleaned ORDER BY user_id").fetchall()
    conn.close()

    assert report["outliers"][0]["affected_rows"] == 1
    assert report["rules"][0]["violations"] == 1
    assert report["cross_table_rules"][0]["violations"] == 1
    assert rows[1][1] is None
    assert rows[1][2] is True
    assert rows[0][3] == "138****5678"
