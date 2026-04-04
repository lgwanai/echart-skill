"""
Test cases for DatabaseRepository with connection pooling and WAL mode.

This module tests the DatabaseRepository class that implements connection
pooling and WAL mode for SQLite databases to support concurrent access.
"""

import pytest
import sqlite3
import tempfile
import os
import threading
from pathlib import Path

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConnectionPoolSize:
    """Test connection pool size configuration."""

    def test_connection_pool_size(self):
        """DatabaseRepository creates pool with specified size.

        Expected behavior:
        - Create repository with pool_size=3
        - Verify 3 connections are available in the pool
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path, pool_size=3)
            # Pool should have 3 connections available
            assert repo._pool.qsize() == 3
            repo.close_all()
        finally:
            os.unlink(db_path)

    def test_connection_pool_default_size(self):
        """DatabaseRepository uses default pool size of 5.

        Expected behavior:
        - Create repository without specifying pool_size
        - Verify 5 connections are available in the pool
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path)
            assert repo._pool.qsize() == 5
            repo.close_all()
        finally:
            os.unlink(db_path)


class TestConnectionContextManager:
    """Test connection context manager behavior."""

    def test_connection_context_manager(self):
        """Connection context manager returns and returns connections.

        Expected behavior:
        - Get connection from pool using context manager
        - Use connection for query
        - Verify connection is returned to pool after context exit
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path, pool_size=2)

            # Get initial pool size
            initial_size = repo._pool.qsize()

            # Use connection via context manager
            with repo.connection() as conn:
                # Pool should have one less connection
                assert repo._pool.qsize() == initial_size - 1
                # Connection should be valid
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1

            # After context exit, connection should be returned
            assert repo._pool.qsize() == initial_size

            repo.close_all()
        finally:
            os.unlink(db_path)

    def test_connection_returned_on_exception(self):
        """Connection is returned to pool even if exception occurs.

        Expected behavior:
        - Get connection from pool
        - Raise exception inside context
        - Verify connection is still returned to pool
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path, pool_size=2)
            initial_size = repo._pool.qsize()

            try:
                with repo.connection() as conn:
                    conn.execute("SELECT 1")
                    raise ValueError("Test exception")
            except ValueError:
                pass

            # Connection should still be returned
            assert repo._pool.qsize() == initial_size

            repo.close_all()
        finally:
            os.unlink(db_path)


class TestWALMode:
    """Test WAL mode configuration."""

    def test_wal_mode_enabled(self):
        """WAL mode is enabled on all connections.

        Expected behavior:
        - Query PRAGMA journal_mode
        - Verify returns 'wal' for all connections
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path, pool_size=3)

            # Check WAL mode on all connections
            for _ in range(3):
                with repo.connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA journal_mode")
                    result = cursor.fetchone()
                    assert result[0].lower() == 'wal'

            repo.close_all()
        finally:
            os.unlink(db_path)

    def test_synchronous_normal(self):
        """SYNCHRONOUS is set to NORMAL for better WAL performance.

        Expected behavior:
        - Query PRAGMA synchronous
        - Verify returns 1 (NORMAL)
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path, pool_size=1)

            with repo.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA synchronous")
                result = cursor.fetchone()
                # NORMAL = 1
                assert result[0] == 1

            repo.close_all()
        finally:
            os.unlink(db_path)


class TestExecuteQuery:
    """Test execute_query method."""

    def test_execute_query(self):
        """execute_query returns list of dicts.

        Expected behavior:
        - Insert test data into table
        - Query with execute_query
        - Verify results are returned as list of dictionaries
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path)

            # Create test table and insert data
            with repo.connection() as conn:
                conn.execute("CREATE TABLE test_data (id INTEGER PRIMARY KEY, name TEXT, value REAL)")
                conn.execute("INSERT INTO test_data (name, value) VALUES ('test1', 100)")
                conn.execute("INSERT INTO test_data (name, value) VALUES ('test2', 200)")
                conn.commit()

            # Query using execute_query
            results = repo.execute_query("SELECT * FROM test_data ORDER BY id")

            assert len(results) == 2
            assert isinstance(results, list)
            assert isinstance(results[0], dict)
            assert results[0]['name'] == 'test1'
            assert results[0]['value'] == 100
            assert results[1]['name'] == 'test2'
            assert results[1]['value'] == 200

            repo.close_all()
        finally:
            os.unlink(db_path)

    def test_execute_query_with_params(self):
        """execute_query supports parameterized queries.

        Expected behavior:
        - Use parameterized query
        - Verify parameters are safely bound
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path)

            with repo.connection() as conn:
                conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, category TEXT)")
                conn.execute("INSERT INTO items (category) VALUES ('A')")
                conn.execute("INSERT INTO items (category) VALUES ('B')")
                conn.execute("INSERT INTO items (category) VALUES ('A')")
                conn.commit()

            results = repo.execute_query(
                "SELECT * FROM items WHERE category = ?",
                ('A',)
            )

            assert len(results) == 2
            assert all(r['category'] == 'A' for r in results)

            repo.close_all()
        finally:
            os.unlink(db_path)

    def test_execute_query_empty_result(self):
        """execute_query returns empty list for no results.

        Expected behavior:
        - Query table with no matching rows
        - Verify empty list is returned
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path)

            with repo.connection() as conn:
                conn.execute("CREATE TABLE empty_table (id INTEGER PRIMARY KEY)")
                conn.commit()

            results = repo.execute_query("SELECT * FROM empty_table")

            assert results == []
            assert isinstance(results, list)

            repo.close_all()
        finally:
            os.unlink(db_path)


class TestExecuteMany:
    """Test execute_many method."""

    def test_execute_many(self):
        """execute_many inserts multiple rows efficiently.

        Expected behavior:
        - Insert 100 rows with execute_many
        - Verify count matches inserted rows
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path)

            # Create test table
            with repo.connection() as conn:
                conn.execute("CREATE TABLE bulk_data (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)")
                conn.commit()

            # Insert 100 rows with execute_many
            rows = [(f"item_{i}", i * 10) for i in range(100)]
            count = repo.execute_many(
                "INSERT INTO bulk_data (name, value) VALUES (?, ?)",
                rows
            )

            assert count == 100

            # Verify all rows were inserted
            results = repo.execute_query("SELECT COUNT(*) as cnt FROM bulk_data")
            assert results[0]['cnt'] == 100

            repo.close_all()
        finally:
            os.unlink(db_path)

    def test_execute_many_update(self):
        """execute_many works for bulk updates.

        Expected behavior:
        - Insert test data
        - Update multiple rows with execute_many
        - Verify updates applied
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path)

            with repo.connection() as conn:
                conn.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, price REAL)")
                conn.execute("INSERT INTO products (id, price) VALUES (1, 10.0)")
                conn.execute("INSERT INTO products (id, price) VALUES (2, 20.0)")
                conn.execute("INSERT INTO products (id, price) VALUES (3, 30.0)")
                conn.commit()

            # Update prices
            updates = [(15.0, 1), (25.0, 2), (35.0, 3)]
            count = repo.execute_many(
                "UPDATE products SET price = ? WHERE id = ?",
                updates
            )

            assert count == 3

            # Verify updates
            results = repo.execute_query("SELECT price FROM products ORDER BY id")
            assert results[0]['price'] == 15.0
            assert results[1]['price'] == 25.0
            assert results[2]['price'] == 35.0

            repo.close_all()
        finally:
            os.unlink(db_path)


class TestConcurrentRead:
    """Test concurrent access."""

    def test_concurrent_read(self):
        """Concurrent access does not cause locking errors.

        Expected behavior:
        - Use threading to read from multiple connections simultaneously
        - Verify no 'database is locked' errors occur
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path, pool_size=5)

            # Create and populate test table
            with repo.connection() as conn:
                conn.execute("CREATE TABLE concurrent_test (id INTEGER PRIMARY KEY, data TEXT)")
                for i in range(100):
                    conn.execute(f"INSERT INTO concurrent_test (data) VALUES ('data_{i}')")
                conn.commit()

            errors = []
            results_list = []

            def read_data():
                try:
                    # Each thread gets its own connection from the pool
                    result = repo.execute_query("SELECT COUNT(*) as cnt FROM concurrent_test")
                    results_list.append(result[0]['cnt'])
                except Exception as e:
                    errors.append(str(e))

            # Launch 10 concurrent reader threads
            threads = []
            for _ in range(10):
                t = threading.Thread(target=read_data)
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            # No errors should have occurred
            assert len(errors) == 0, f"Concurrent access errors: {errors}"
            # All threads should have read the same count
            assert len(results_list) == 10
            assert all(c == 100 for c in results_list)

            repo.close_all()
        finally:
            os.unlink(db_path)

    def test_concurrent_read_write(self):
        """Concurrent read and write operations work with WAL mode.

        Expected behavior:
        - One thread writes while others read
        - No locking errors occur
        - Readers see consistent data
        """
        from database import DatabaseRepository
        import time

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path, pool_size=5)

            # Create initial table
            with repo.connection() as conn:
                conn.execute("CREATE TABLE rw_test (id INTEGER PRIMARY KEY, value INTEGER)")
                conn.commit()

            errors = []
            write_complete = []

            def write_data():
                try:
                    for i in range(50):
                        with repo.connection() as conn:
                            conn.execute(f"INSERT INTO rw_test (value) VALUES ({i})")
                            conn.commit()
                        time.sleep(0.001)  # Small delay to allow interleaving
                    write_complete.append(True)
                except Exception as e:
                    errors.append(f"Write error: {e}")

            def read_data():
                try:
                    for _ in range(10):
                        repo.execute_query("SELECT COUNT(*) as cnt FROM rw_test")
                        time.sleep(0.01)
                except Exception as e:
                    errors.append(f"Read error: {e}")

            # Start writer thread
            writer = threading.Thread(target=write_data)
            writer.start()

            # Start reader threads
            readers = []
            for _ in range(3):
                t = threading.Thread(target=read_data)
                readers.append(t)
                t.start()

            writer.join()
            for t in readers:
                t.join()

            # No errors should have occurred
            assert len(errors) == 0, f"Concurrent R/W errors: {errors}"
            assert len(write_complete) == 1

            # Verify final count
            results = repo.execute_query("SELECT COUNT(*) as cnt FROM rw_test")
            assert results[0]['cnt'] == 50

            repo.close_all()
        finally:
            os.unlink(db_path)


class TestCloseAll:
    """Test close_all method."""

    def test_close_all(self):
        """close_all closes all connections in the pool.

        Expected behavior:
        - Create repository with multiple connections
        - Call close_all
        - Verify pool is empty and connections are closed
        """
        from database import DatabaseRepository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            repo = DatabaseRepository(db_path, pool_size=3)

            # Pool should have connections
            assert repo._pool.qsize() == 3

            # Close all
            repo.close_all()

            # Pool should be empty
            assert repo._pool.qsize() == 0
        finally:
            os.unlink(db_path)


class TestGetRepository:
    """Test module-level singleton."""

    def test_get_repository_singleton(self):
        """get_repository returns the same instance.

        Expected behavior:
        - Call get_repository multiple times
        - Verify same instance is returned
        """
        from database import get_repository, _repo

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            # Reset singleton
            import database
            database._repo = None

            repo1 = get_repository(db_path)
            repo2 = get_repository(db_path)

            assert repo1 is repo2

            repo1.close_all()
        finally:
            # Reset singleton for other tests
            import database
            database._repo = None
            os.unlink(db_path)

    def test_get_repository_creates_new(self):
        """get_repository creates new instance if none exists.

        Expected behavior:
        - Reset singleton to None
        - Call get_repository
        - Verify new instance is created
        """
        from database import get_repository

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            # Reset singleton
            import database
            database._repo = None

            repo = get_repository(db_path)

            assert repo is not None
            assert hasattr(repo, 'connection')
            assert hasattr(repo, 'execute_query')

            repo.close_all()
        finally:
            # Reset singleton for other tests
            import database
            database._repo = None
            os.unlink(db_path)
