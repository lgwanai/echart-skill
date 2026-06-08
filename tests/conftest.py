import pytest
import duckdb
import tempfile
import os
from pathlib import Path


@pytest.fixture(autouse=True)
def reset_database_singleton():
    """Reset database singleton before and after each test."""
    import database
    database._cleanup_repo()
    yield
    database._cleanup_repo()


@pytest.fixture
def temp_db():
    """Create a temporary DuckDB database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.duckdb', delete=False) as f:
        db_path = f.name

    os.unlink(db_path)
    conn = duckdb.connect(db_path)
    conn.execute('''
        CREATE TABLE test_data (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value REAL
        )
    ''')
    conn.execute("INSERT INTO test_data (id, name, value) VALUES (1, 'test1', 100)")
    conn.execute("INSERT INTO test_data (id, name, value) VALUES (2, 'test2', 200)")
    conn.commit()
    conn.close()

    yield db_path

    os.unlink(db_path)


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for output files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_config():
    """Sample chart configuration for testing."""
    return {
        "db_path": "workspace.duckdb",
        "query": "SELECT name, value FROM test_data",
        "title": "Test Chart",
        "output_path": "tmp/test_chart.html"
    }
