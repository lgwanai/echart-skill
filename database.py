"""
DatabaseRepository with connection pooling for DuckDB.

This module provides a thread-safe DuckDB repository with connection pooling
to support concurrent read/write access in multi-agent scenarios.

Features:
- List-based connection pool with threading lock for write serialization
- DuckDB's single-writer model protected by threading.Lock
- Context manager for safe connection handling
- High-level methods for common operations
"""

import duckdb
import threading
import atexit
from contextlib import contextmanager
from typing import Iterator, Any, Optional


class DatabaseRepository:
    """Thread-safe DuckDB repository with connection pooling.

    This class manages a pool of DuckDB connections with thread-safe
    write serialization, allowing concurrent read and write operations
    from multiple threads.

    Attributes:
        _db_path: Path to the DuckDB database file.
        _pool: List-based connection pool.
        _lock: Thread lock for write serialization.

    Example:
        >>> repo = DatabaseRepository("workspace.duckdb", pool_size=5)
        >>> with repo.connection() as conn:
        ...     conn.execute("SELECT * FROM users")
        ...     print(conn.fetchall())
        >>> repo.close_all()
    """

    def __init__(self, db_path: str, pool_size: int = 5):
        """Initialize the database repository with connection pool.

        Args:
            db_path: Path to the DuckDB database file.
            pool_size: Number of connections in the pool (default: 5).
        """
        self._db_path = db_path
        self._pool: list[duckdb.DuckDBPyConnection] = []
        self._lock = threading.Lock()
        self._initialize_pool(pool_size)

    def _initialize_pool(self, size: int) -> None:
        """Create connection pool with DuckDB configuration.

        Each connection is configured with:
        - threads=4: Parallel query execution
        - memory_limit=2GB: Memory usage cap

        Args:
            size: Number of connections to create.
        """
        for _ in range(size):
            conn = self._create_connection()
            self._pool.append(conn)

    def _create_connection(self) -> duckdb.DuckDBPyConnection:
        """Create a single DuckDB connection with optimal settings.

        Returns:
            duckdb.DuckDBPyConnection: A configured DuckDB connection.
        """
        conn = duckdb.connect(self._db_path)
        conn.execute("SET threads=4")
        conn.execute("SET memory_limit='2GB'")
        return conn

    @contextmanager
    def connection(self) -> Iterator[duckdb.DuckDBPyConnection]:
        """Get a connection from the pool as a context manager.

        The connection is automatically returned to the pool when the
        context exits, even if an exception occurs.

        Yields:
            duckdb.DuckDBPyConnection: A database connection from the pool.

        Example:
            >>> with repo.connection() as conn:
            ...     conn.execute("SELECT 1")
        """
        with self._lock:
            conn = self._pool.pop()
        try:
            yield conn
        finally:
            with self._lock:
                self._pool.append(conn)

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
            if params:
                conn.execute(query, params)
            else:
                conn.execute(query)
            columns = [desc[0] for desc in conn.description]
            rows = conn.fetchall()
            return [dict(zip(columns, row)) for row in rows]

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
            conn.executemany(query, params_list)
            return conn.rowcount

    def close_all(self) -> None:
        """Close all connections in the pool.

        This method should be called when the repository is no longer
        needed to release database resources.
        """
        with self._lock:
            for conn in self._pool:
                conn.close()
            self._pool.clear()


# Module-level singleton for backward compatibility
_repo: Optional[DatabaseRepository] = None


def get_repository(db_path: str = "workspace.duckdb") -> DatabaseRepository:
    """Get or create the database repository singleton.

    This function provides a convenient way to access a shared
    DatabaseRepository instance across the application.

    Args:
        db_path: Path to the DuckDB database file (default: "workspace.duckdb").

    Returns:
        DatabaseRepository: The singleton repository instance.

    Example:
        >>> repo = get_repository("workspace.duckdb")
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
