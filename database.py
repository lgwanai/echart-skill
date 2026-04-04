"""
DatabaseRepository with connection pooling and WAL mode for SQLite.

This module provides a thread-safe SQLite repository with connection pooling
to support concurrent read/write access in multi-agent scenarios.

Features:
- Queue-based connection pool (thread-safe)
- WAL mode enabled for concurrent read/write
- Context manager for safe connection handling
- High-level methods for common operations
"""

import sqlite3
import atexit
from contextlib import contextmanager
from queue import Queue
from typing import Iterator, Any, Optional


class DatabaseRepository:
    """Thread-safe SQLite repository with connection pooling and WAL mode.

    This class manages a pool of SQLite connections with WAL mode enabled,
    allowing concurrent read and write operations from multiple threads.

    Attributes:
        _db_path: Path to the SQLite database file.
        _pool: Queue-based connection pool.
        _lock: Thread lock for pool initialization.

    Example:
        >>> repo = DatabaseRepository("workspace.db", pool_size=5)
        >>> with repo.connection() as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM users")
        ...     print(cursor.fetchall())
        >>> repo.close_all()
    """

    def __init__(self, db_path: str, pool_size: int = 5):
        """Initialize the database repository with connection pool.

        Args:
            db_path: Path to the SQLite database file.
            pool_size: Number of connections in the pool (default: 5).
        """
        self._db_path = db_path
        self._pool: Queue[sqlite3.Connection] = Queue(maxsize=pool_size)
        self._initialize_pool(pool_size)

    def _initialize_pool(self, size: int) -> None:
        """Create connection pool with WAL mode enabled.

        Each connection is configured with:
        - check_same_thread=False: Required for pool usage
        - WAL mode: Allows concurrent readers with writers
        - synchronous=NORMAL: Better performance with WAL
        - Row factory: Returns dict-like rows

        Args:
            size: Number of connections to create.
        """
        for _ in range(size):
            conn = sqlite3.connect(
                self._db_path,
                check_same_thread=False,  # Required for pool
                timeout=5.0
            )
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for concurrent read/write
            conn.execute("PRAGMA journal_mode=WAL")
            # NORMAL is faster with WAL, still safe
            conn.execute("PRAGMA synchronous=NORMAL")
            self._pool.put(conn)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Get a connection from the pool as a context manager.

        The connection is automatically returned to the pool when the
        context exits, even if an exception occurs.

        Yields:
            sqlite3.Connection: A database connection from the pool.

        Example:
            >>> with repo.connection() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT 1")
        """
        conn = self._pool.get()
        try:
            yield conn
        finally:
            self._pool.put(conn)

    def execute_query(self, query: str, params: tuple = ()) -> list[dict]:
        """Execute a parameterized SELECT query and return results.

        Args:
            query: SQL query string (SELECT statements).
            params: Query parameters (default: empty tuple).

        Returns:
            List of dictionaries, one per row.

        Example:
            >>> results = repo.execute_query(
            ...     "SELECT * FROM users WHERE age > ?",
            ...     (18,)
            ... )
        """
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_many(self, query: str, params_list: list[tuple]) -> int:
        """Execute many INSERT/UPDATE operations efficiently.

        This method uses executemany for batch operations, which is
        more efficient than individual execute calls.

        Args:
            query: SQL query string (INSERT/UPDATE statements).
            params_list: List of parameter tuples.

        Returns:
            Number of rows affected.

        Example:
            >>> count = repo.execute_many(
            ...     "INSERT INTO users (name, age) VALUES (?, ?)",
            ...     [("Alice", 25), ("Bob", 30)]
            ... )
        """
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

    def close_all(self) -> None:
        """Close all connections in the pool.

        This method should be called when the repository is no longer
        needed to release database resources.
        """
        while not self._pool.empty():
            conn = self._pool.get()
            conn.close()


# Module-level singleton for backward compatibility
_repo: Optional[DatabaseRepository] = None


def get_repository(db_path: str = "workspace.db") -> DatabaseRepository:
    """Get or create the database repository singleton.

    This function provides a convenient way to access a shared
    DatabaseRepository instance across the application.

    Args:
        db_path: Path to the SQLite database file (default: "workspace.db").

    Returns:
        DatabaseRepository: The singleton repository instance.

    Example:
        >>> repo = get_repository("workspace.db")
        >>> with repo.connection() as conn:
        ...     conn.execute("SELECT 1")
    """
    global _repo
    if _repo is None:
        _repo = DatabaseRepository(db_path)
        # Register cleanup on program exit
        atexit.register(_cleanup_repo)
    return _repo


def _cleanup_repo() -> None:
    """Cleanup function registered with atexit."""
    global _repo
    if _repo is not None:
        _repo.close_all()
        _repo = None
