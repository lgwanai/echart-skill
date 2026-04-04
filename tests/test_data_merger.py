"""Tests for DataMerger class.

This module tests the data merger functionality including:
- MergeConfig validation (empty, single, duplicates, valid names)
- DataMerger initialization and source table validation
- Merge operations with _source_table column
- Save to database functionality
"""

import pytest
import sqlite3
import tempfile
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.data_merger import MergeConfig, DataMerger


class TestMergeConfig:
    """Tests for MergeConfig pydantic model."""

    def test_rejects_empty_source_tables(self):
        """MergeConfig should reject empty source_tables list."""
        with pytest.raises(ValueError, match="at least 2"):
            MergeConfig(
                source_tables=[],
                target_table="merged_table"
            )

    def test_rejects_single_table(self):
        """MergeConfig should reject single table (need at least 2)."""
        with pytest.raises(ValueError, match="at least 2"):
            MergeConfig(
                source_tables=["table1"],
                target_table="merged_table"
            )

    def test_rejects_duplicate_table_names(self):
        """MergeConfig should reject duplicate table names."""
        with pytest.raises(ValueError, match="Duplicate"):
            MergeConfig(
                source_tables=["table1", "table1", "table2"],
                target_table="merged_table"
            )

    def test_rejects_invalid_table_name(self):
        """MergeConfig should reject invalid table names."""
        with pytest.raises(ValueError, match="invalid|reserved|SQL"):
            MergeConfig(
                source_tables=["123_invalid", "table2"],
                target_table="merged_table"
            )

    def test_rejects_sql_reserved_word_as_table_name(self):
        """MergeConfig should reject SQL reserved words as table names."""
        with pytest.raises(ValueError, match="reserved|SQL"):
            MergeConfig(
                source_tables=["select", "table2"],
                target_table="merged_table"
            )

    def test_accepts_valid_config(self):
        """MergeConfig should accept valid configuration."""
        config = MergeConfig(
            source_tables=["table1", "table2"],
            target_table="merged_table"
        )
        assert config.source_tables == ["table1", "table2"]
        assert config.target_table == "merged_table"
        assert config.db_path == "workspace.db"

    def test_accepts_custom_db_path(self):
        """MergeConfig should accept custom db_path."""
        config = MergeConfig(
            source_tables=["table1", "table2"],
            target_table="merged_table",
            db_path="custom.db"
        )
        assert config.db_path == "custom.db"


class TestDataMerger:
    """Tests for DataMerger class."""

    @pytest.fixture
    def temp_db_with_tables(self):
        """Create a temporary database with test tables."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        conn = sqlite3.connect(db_path)

        # Create test tables
        conn.execute('''
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT,
                city TEXT
            )
        ''')
        conn.execute("INSERT INTO customers (name, city) VALUES ('Alice', 'Beijing')")
        conn.execute("INSERT INTO customers (name, city) VALUES ('Bob', 'Shanghai')")

        conn.execute('''
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                product TEXT,
                amount REAL
            )
        ''')
        conn.execute("INSERT INTO orders (product, amount) VALUES ('Widget', 99.99)")
        conn.execute("INSERT INTO orders (product, amount) VALUES ('Gadget', 149.99)")

        conn.commit()
        conn.close()

        yield db_path

        os.unlink(db_path)

    def test_initializes_with_valid_config(self):
        """DataMerger should initialize with valid MergeConfig."""
        config = MergeConfig(
            source_tables=["table1", "table2"],
            target_table="merged_table"
        )
        merger = DataMerger(config)
        assert merger.config == config

    def test_validates_source_tables_exist(self, temp_db_with_tables):
        """DataMerger should validate that source tables exist."""
        config = MergeConfig(
            source_tables=["customers", "orders"],
            target_table="merged_data",
            db_path=temp_db_with_tables
        )
        merger = DataMerger(config)
        # Should not raise
        merger.validate_source_tables()

    def test_raises_for_nonexistent_source_table(self, temp_db_with_tables):
        """DataMerger should raise error for non-existent source table."""
        config = MergeConfig(
            source_tables=["customers", "nonexistent"],
            target_table="merged_data",
            db_path=temp_db_with_tables
        )
        merger = DataMerger(config)
        with pytest.raises(ValueError, match="not found|does not exist"):
            merger.validate_source_tables()

    def test_merge_tables_returns_dataframe(self, temp_db_with_tables):
        """DataMerger should return merged DataFrame with _source_table column."""
        config = MergeConfig(
            source_tables=["customers", "orders"],
            target_table="merged_data",
            db_path=temp_db_with_tables
        )
        merger = DataMerger(config)
        merged = merger.merge_tables()

        assert len(merged) == 4  # 2 customers + 2 orders
        assert '_source_table' in merged.columns
        assert set(merged['_source_table'].unique()) == {'customers', 'orders'}

    def test_save_to_database_creates_table(self, temp_db_with_tables):
        """DataMerger should save merged data to new table."""
        config = MergeConfig(
            source_tables=["customers", "orders"],
            target_table="merged_data",
            db_path=temp_db_with_tables
        )
        merger = DataMerger(config)
        merged = merger.merge_tables()
        merger.save_to_database(merged)

        # Verify table exists and has correct data
        conn = sqlite3.connect(temp_db_with_tables)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM merged_data")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 4
