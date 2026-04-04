# Architecture Research

**Domain:** Python Data Analysis Tool (Local-first, Agent Skill Pack)
**Researched:** 2026-04-04
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
+------------------------------------------------------------------+
|                        ENTRY POINTS                               |
|   +----------------+      +----------------+      +-------------+ |
|   | Agent Workflow |      | CLI Commands   |      | HTTP Server | |
|   | (SKILL.md)     |      | (argparse)     |      | (aiohttp)   | |
|   +-------+--------+      +-------+--------+      +------+------+ |
|           |                       |                       |        |
+-----------|-----------------------|-----------------------|--------+
            |                       |                       |
            v                       v                       v
+------------------------------------------------------------------+
|                     CORE SERVICES LAYER                          |
|  +----------------+  +----------------+  +------------------+    |
|  | DataImporter   |  | ChartGenerator |  | DataExporter     |    |
|  | (streaming)    |  | (async geo)    |  | (format support) |    |
|  +-------+--------+  +-------+--------+  +--------+---------+    |
|          |                   |                    |              |
+----------|-------------------|--------------------|--------------+
           |                   |                    |
           v                   v                    v
+------------------------------------------------------------------+
|                    REPOSITORY LAYER (NEW)                         |
|  +----------------------------------------------------------------+|
|  | DatabaseRepository                                              ||
|  | - Connection pooling (context manager)                         ||
|  | - Transaction management                                        ||
|  | - Query execution                                               ||
|  +----------------------------------------------------------------+|
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                       DATA LAYER                                  |
|  +------------------+  +------------------+  +------------------+ |
|  | SQLite Database  |  | File System      |  | Cache (geo)      | |
|  | (workspace.db)   |  | (imports/output) |  | (geo_cache.json) | |
|  +------------------+  +------------------+  +------------------+ |
+------------------------------------------------------------------+
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| DataImporter | Ingest data from files into SQLite | Streaming with pandas chunksize, async for large files |
| ChartGenerator | Generate ECharts HTML visualizations | Template-driven with async geocoding API calls |
| DataExporter | Export SQLite data to CSV/Excel | pandas DataFrame with format-specific options |
| DataCleaner | Cleanup old tables, manage retention | SQL-based with metadata tracking |
| MetricsManager | Store business metric definitions | Simple CRUD with metadata table |
| Server | Local HTTP server for chart files | aiohttp async server with CORS |
| DatabaseRepository | Abstract database operations | Context manager + connection pooling |

## Recommended Project Structure

```
echart-skill/
+-- src/
|   +-- echart_skill/                    # Main package
|       +-- __init__.py
|       +-- core/                        # Core business logic
|       |   +-- __init__.py
|       |   +-- importer.py              # DataImporter (streaming)
|       |   +-- exporter.py              # DataExporter
|       |   +-- chart_generator.py       # ChartGenerator
|       |   +-- cleaner.py               # DataCleaner
|       |   +-- metrics.py               # MetricsManager
|       |
|       +-- database/                    # Database layer (NEW)
|       |   +-- __init__.py
|       |   +-- repository.py            # DatabaseRepository
|       |   +-- connection.py            # Connection pooling
|       |   +-- models.py                # Data models/metadata
|       |
|       +-- server/                      # HTTP server (NEW: async)
|       |   +-- __init__.py
|       |   +-- app.py                   # aiohttp Application
|       |   +-- handlers.py              # Request handlers
|       |   +-- middleware.py            # CORS, logging
|       |
|       +-- utils/                       # Shared utilities
|       |   +-- __init__.py
|       |   +-- geocoding.py             # Async geocoding
|       |   +-- validation.py            # Input validation
|       |   +-- logging_config.py        # Structured logging
|       |
|       +-- templates/                   # Chart templates
|           +-- base_html.py             # HTML generation
|
+-- references/                          # Static assets
|   +-- prompts/                         # ECharts prompt templates
|   +-- maps/                            # Offline map resources
|
+-- tests/                               # Test suite (NEW)
|   +-- conftest.py                      # Shared fixtures
|   +-- unit/
|   |   +-- test_importer.py
|   |   +-- test_exporter.py
|   |   +-- test_chart_generator.py
|   |   +-- test_repository.py
|   |
|   +-- integration/
|   |   +-- test_full_pipeline.py
|   |   +-- test_server.py
|   |
|   +-- fixtures/
|       +-- sample_data/                 # Test data files
|
+-- scripts/                             # Legacy CLI entry points (migration)
+-- pyproject.toml                       # Project config, dependencies
+-- pytest.ini                           # pytest configuration
```

### Structure Rationale

- **src/ layout:** Prevents import issues, standard for Python packages
- **core/:** Business logic isolated from infrastructure
- **database/:** Repository pattern enables testability and connection management
- **server/:** Async HTTP server isolated for performance
- **tests/:** Mirror src/ structure for discoverability

## Architectural Patterns

### Pattern 1: Repository Pattern for Database Access

**What:** Abstract database operations behind a repository interface. All SQL goes through this layer.

**When to use:** Always - enables testability, connection management, and SQL injection prevention.

**Trade-offs:**
- Pros: Testable (mock repository), connection pooling, transaction management
- Cons: Small abstraction overhead

**Example:**
```python
# database/repository.py
from contextlib import contextmanager
from typing import Iterator, Any
import sqlite3
from queue import Queue

class DatabaseRepository:
    """Thread-safe SQLite repository with connection pooling."""

    def __init__(self, db_path: str, pool_size: int = 5):
        self._db_path = db_path
        self._pool: Queue[sqlite3.Connection] = Queue(maxsize=pool_size)
        self._initialize_pool(pool_size)

    def _initialize_pool(self, size: int) -> None:
        for _ in range(size):
            conn = sqlite3.connect(self._db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._pool.put(conn)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Get a connection from the pool."""
        conn = self._pool.get()
        try:
            yield conn
        finally:
            self._pool.put(conn)

    def execute_query(self, query: str, params: tuple = ()) -> list[dict]:
        """Execute a parameterized query safely."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_insert(self, table: str, data: dict) -> None:
        """Insert data safely with parameterized query."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        with self.connection() as conn:
            conn.cursor().execute(query, tuple(data.values()))
            conn.commit()
```

### Pattern 2: Streaming Import for Large Files

**What:** Process large files in chunks rather than loading entirely into memory.

**When to use:** Files > 100MB, or when memory constraints exist.

**Trade-offs:**
- Pros: Constant memory usage regardless of file size
- Cons: Slightly slower for small files, more complex code

**Example:**
```python
# core/importer.py
from typing import Iterator
import pandas as pd

class DataImporter:
    CHUNK_SIZE = 50_000  # rows per chunk

    def import_csv_streaming(
        self,
        file_path: str,
        table_name: str,
        repo: DatabaseRepository
    ) -> int:
        """Import CSV in chunks, yielding progress."""
        total_rows = 0
        first_chunk = True

        for chunk in pd.read_csv(file_path, chunksize=self.CHUNK_SIZE):
            if first_chunk:
                self._create_table_from_df(chunk, table_name, repo)
                first_chunk = False

            self._insert_chunk(chunk, table_name, repo)
            total_rows += len(chunk)
            yield total_rows  # Progress reporting

        return total_rows

    def _insert_chunk(
        self,
        chunk: pd.DataFrame,
        table: str,
        repo: DatabaseRepository
    ) -> None:
        """Insert a chunk using parameterized queries."""
        columns = chunk.columns.tolist()
        placeholders = ', '.join('?' * len(columns))
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

        with repo.connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, chunk.values.tolist())
            conn.commit()
```

### Pattern 3: Async API Calls with aiohttp

**What:** Use asyncio and aiohttp for concurrent API calls (geocoding).

**When to use:** Multiple independent HTTP requests, I/O-bound operations.

**Trade-offs:**
- Pros: Significant speedup for multiple requests, non-blocking
- Cons: Adds async complexity, requires async throughout call stack

**Example:**
```python
# utils/geocoding.py
import aiohttp
import asyncio
from typing import Optional
import json

class AsyncGeocoder:
    def __init__(self, ak: str, cache_path: str):
        self._ak = ak
        self._cache_path = cache_path
        self._cache = self._load_cache()
        self._session: Optional[aiohttp.ClientSession] = None

    def _load_cache(self) -> dict:
        try:
            with open(self._cache_path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()

    async def geocode(self, address: str) -> Optional[list[float]]:
        """Async geocode with caching."""
        if address in self._cache:
            return self._cache[address]

        url = f"https://api.map.baidu.com/geocoding/v3/"
        params = {
            "address": address,
            "output": "json",
            "ak": self._ak
        }

        async with self._session.get(url, params=params) as resp:
            data = await resp.json()
            if data.get("status") == 0:
                loc = data["result"]["location"]
                coord = [loc["lng"], loc["lat"]]
                self._cache[address] = coord
                return coord
        return None

    async def geocode_batch(self, addresses: list[str]) -> dict[str, list[float]]:
        """Geocode multiple addresses concurrently."""
        async with self as geocoder:
            tasks = [geocoder.geocode(addr) for addr in addresses]
            results = await asyncio.gather(*tasks)
            return dict(zip(addresses, results))
```

### Pattern 4: Test Architecture with pytest Fixtures

**What:** Use pytest fixtures for test isolation, database setup, and cleanup.

**When to use:** All tests requiring database or external resources.

**Trade-offs:**
- Pros: Isolated tests, reusable setup, automatic cleanup
- Cons: Initial fixture setup complexity

**Example:**
```python
# tests/conftest.py
import pytest
import tempfile
import os
from echart_skill.database.repository import DatabaseRepository
from echart_skill.core.importer import DataImporter

@pytest.fixture
def temp_db():
    """Create a temporary database for each test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    os.unlink(db_path)  # Cleanup after test

@pytest.fixture
def repo(temp_db):
    """Create a repository with connection pooling."""
    return DatabaseRepository(temp_db, pool_size=3)

@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing."""
    csv_path = tmp_path / "test_data.csv"
    csv_path.write_text("name,value\nAlice,100\nBob,200\n")
    return str(csv_path)

@pytest.fixture
def importer(repo):
    """Create an importer with injected repository."""
    return DataImporter(repo)

# tests/unit/test_importer.py
def test_import_csv_creates_table(importer, sample_csv, repo):
    """Test that CSV import creates the expected table."""
    # Act
    list(importer.import_csv_streaming(sample_csv, "test_table", repo))

    # Assert
    result = repo.execute_query(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    table_names = [r["name"] for r in result]
    assert "test_table" in table_names

def test_import_csv_data_correct(importer, sample_csv, repo):
    """Test that imported data matches source."""
    list(importer.import_csv_streaming(sample_csv, "test_table", repo))

    rows = repo.execute_query("SELECT * FROM test_table ORDER BY name")
    assert len(rows) == 2
    assert rows[0]["name"] == "Alice"
    assert rows[0]["value"] == 100
```

## Data Flow

### Request Flow (Import)

```
[Agent/CLI]
    |
    v
[DataImporter.import_csv_streaming()]
    |
    v
+-----------------------+
| For each chunk:       |
|   1. Read chunk       |<-- pandas.read_csv(chunksize=50000)
|   2. Validate data    |
|   3. Clean columns    |
|   4. Insert via repo  |--> DatabaseRepository.execute_insert()
|   5. Yield progress   |
+-----------------------+
    |
    v
[DatabaseRepository.connection()]
    |
    v
[SQLite Connection Pool] --(returns connection)--> [Execute query]
    |
    v
[Metadata record in _data_skill_meta]
```

### Request Flow (Chart Generation)

```
[Agent/CLI]
    |
    v
[ChartGenerator.generate()]
    |
    v
[DatabaseRepository.execute_query()] --> SQLite
    |
    v
[AsyncGeocoder.geocode_batch()] --> aiohttp (if map chart)
    |         |
    |         v
    |    [Concurrent API calls] --> Baidu Geocoding API
    |         |
    +---------+
    |
    v
[ECharts HTML Generation]
    |
    v
[Server.serve_file()] --> aiohttp server
    |
    v
[Return URL to Agent]
```

### Key Data Flows

1. **Import Flow:** File -> Chunked Reader -> Validation -> Repository -> SQLite (streaming, constant memory)
2. **Query Flow:** Agent SQL -> Repository (parameterized) -> SQLite -> DataFrame -> Chart
3. **Geocoding Flow:** Address -> Cache Check -> Async API (if miss) -> Cache Update
4. **Export Flow:** Table/Query -> Repository -> DataFrame -> File Format Writer

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Single user, <100MB files | Current architecture sufficient |
| Single user, >1GB files | Streaming import essential, consider SQLite WAL mode |
| Multiple concurrent imports | Connection pool (5-10 connections), async server |
| High chart generation volume | Async geocoding with rate limiting, chart caching |

### Scaling Priorities

1. **First bottleneck:** Large file imports (memory)
   - Fix: Streaming import with chunksize

2. **Second bottleneck:** Geocoding API latency (100+ addresses)
   - Fix: Async batch geocoding with aiohttp

3. **Third bottleneck:** Database connection contention
   - Fix: Connection pooling with context managers

## Anti-Patterns

### Anti-Pattern 1: Direct sqlite3.connect() in Functions

**What people do:** Call `sqlite3.connect()` in each function that needs database access.

**Why it's wrong:**
- No connection reuse (overhead per call)
- No transaction management
- Hard to test (can't mock)
- Connection leaks if not closed

**Do this instead:** Use Repository pattern with connection pooling:

```python
# BAD
def get_data(db_path: str, table: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)  # New connection every call
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()  # Easy to forget
    return df

# GOOD
def get_data(repo: DatabaseRepository, table: str) -> pd.DataFrame:
    return repo.execute_query(f"SELECT * FROM {table}")  # Pooled, parameterized
```

### Anti-Pattern 2: Synchronous API Calls in Loop

**What people do:** Call `urllib.request.urlopen()` in a for loop for multiple addresses.

**Why it's wrong:** Sequential blocking calls - 100 addresses x 200ms = 20 seconds.

**Do this instead:** Use aiohttp with asyncio.gather for concurrent calls:

```python
# BAD
def geocode_all(addresses: list) -> dict:
    results = {}
    for addr in addresses:
        results[addr] = geocode_sync(addr)  # Blocking!
    return results

# GOOD
async def geocode_all(addresses: list) -> dict:
    async with AsyncGeocoder(ak, cache_path) as geocoder:
        return await geocoder.geocode_batch(addresses)  # Concurrent!
```

### Anti-Pattern 3: Loading Entire File into Memory

**What people do:** Call `pd.read_csv()` without chunksize for large files.

**Why it's wrong:** 1GB file = 1GB+ in memory, causes OOM on large files.

**Do this instead:** Use chunksize for streaming:

```python
# BAD
df = pd.read_csv("large_file.csv")  # Loads everything
df.to_sql("table", conn)

# GOOD
for chunk in pd.read_csv("large_file.csv", chunksize=50000):
    chunk.to_sql("table", conn, if_exists="append")
```

### Anti-Pattern 4: String Formatting in SQL Queries

**What people do:** Use f-strings or string concatenation in SQL queries.

**Why it's wrong:** SQL injection vulnerability, harder to debug.

**Do this instead:** Use parameterized queries:

```python
# BAD - SQL injection risk!
query = f"SELECT * FROM {table_name}"  # table_name could be malicious

# GOOD - Parameterized
query = "SELECT * FROM ?"  # Doesn't work for table names in SQLite
# Instead: validate table name against whitelist, then use f-string for table name only
query = f"SELECT * FROM {validated_table_name}"
# For values, always use parameters:
query = "SELECT * FROM users WHERE name = ?"
cursor.execute(query, (user_input,))
```

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Baidu Geocoding API | aiohttp async client | Rate limit: 30 QPS, cache aggressively |
| ECharts Library | Local bundled copy | No CDN dependency for offline use |
| Map Resources | Local files | China provinces, world maps bundled |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Core <-> Database | Repository interface | All SQL through repository, inject for testing |
| Core <-> Server | File system | Charts written to outputs/, server serves files |
| Agent <-> Core | Function calls | Agent workflow calls core functions directly |

## Migration Path from Current Architecture

### Phase 1: Foundation (Testability)
1. Create `DatabaseRepository` class
2. Refactor all `sqlite3.connect()` calls to use repository
3. Set up `pytest` with `conftest.py` fixtures
4. Write unit tests for core functions

### Phase 2: Performance
1. Implement streaming import in `DataImporter`
2. Add connection pooling to `DatabaseRepository`
3. Create `AsyncGeocoder` utility
4. Refactor chart generator to use async geocoding

### Phase 3: Async Server
1. Create `aiohttp` application in `server/`
2. Migrate HTTP handlers from `http.server`
3. Add structured logging throughout
4. Integration tests for full pipeline

## Sources

- [SQLAlchemy Connection Pooling Documentation](https://docs.sqlalchemy.org/en/20/core/pooling.html) - Connection pool patterns
- [pandas.read_csv chunksize](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) - Streaming file reads
- [pytest fixtures documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html) - Test isolation patterns
- [aiohttp Client Documentation](https://docs.aiohttp.org/en/stable/client.html) - Async HTTP client
- [Python asyncio.gather](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather) - Concurrent execution
- [Python contextlib.contextmanager](https://docs.python.org/3/library/contextlib.html) - Resource management
- [Repository Pattern in Python](https://martinfowler.com/eaaCatalog/repository.html) - Data access abstraction
- [SQLite WAL Mode](https://www.sqlite.org/wal.html) - Concurrent read/write performance
- [pytest tmp_path fixture](https://docs.pytest.org/en/stable/how-to/tmp_path.html) - Temporary files in tests

---

*Architecture research for: Python Data Analysis Tool*
*Researched: 2026-04-04*
