import pytest
import sqlite3
import tempfile
import os
from pathlib import Path


@pytest.fixture(autouse=True)
def reset_database_singleton():
    """Reset database singleton before and after each test."""
    import database
    database._repo = None
    yield
    database._repo = None


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE test_data (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value REAL
        )
    ''')
    conn.execute("INSERT INTO test_data (name, value) VALUES ('test1', 100)")
    conn.execute("INSERT INTO test_data (name, value) VALUES ('test2', 200)")
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
        "db_path": "workspace.db",
        "query": "SELECT name, value FROM test_data",
        "title": "Test Chart",
        "output_path": "tmp/test_chart.html"
    }
