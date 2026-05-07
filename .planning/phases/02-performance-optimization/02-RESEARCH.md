# Phase 2: Performance Optimization - Research

**Researched:** 2026-04-04
**Domain:** SQLite connection pooling, streaming file import, async HTTP geocoding, process lifecycle management
**Confidence:** HIGH (based on existing codebase analysis, STACK.md research, and PITFALLS.md documentation)

## Summary

This phase optimizes system performance to handle large datasets (100MB+ files) and concurrent operations. The codebase currently has: (1) scattered `sqlite3.connect()` calls without pooling or WAL mode, (2) Excel files loaded entirely into memory via openpyxl without streaming, (3) synchronous urllib.request calls for geocoding that block on each request, and (4) server processes without PID tracking or cleanup. The optimization strategy follows the decisions locked in CONTEXT.md: streaming import with 10,000-row chunks, connection pool of 5 connections with WAL mode, 5 concurrent async geocoding requests with retry logic, and PID-based server lifecycle management.

**Primary recommendation:** Create `DatabaseRepository` class with connection pooling and WAL mode, implement streaming Excel import with openpyxl read_only mode, convert geocoding to async httpx with tenacity retry, and add PID file tracking for server process lifecycle.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**大文件处理策略**
- **流式导入：** 始终使用流式导入 — 避免 Excel 文件内存问题
- **分块大小：** 10,000 行/块 — 每块约 1-2MB，平衡内存和性能
- **CSV 处理：** 已有分块导入（chunksize=50000），保持现有逻辑

**连接池配置**
- **连接池大小：** 5 个连接 — 单进程场景足够
- **WAL 模式：** 启用 — 允许读写并发，多 Agent 同时访问数据库
- **连接超时：** 使用默认 5 秒

**异步 API 配置**
- **并发数：** 5 并发 — 百度 API 默认 QPS 限制
- **重试策略：** 3 次重试，指数退避（1s, 2s, 4s）
- **超时时间：** 10 秒单次请求超时
- **使用 httpx 异步客户端**

**服务进程管理**
- **PID 文件位置：** outputs/pids/ — 与其他输出文件一致
- **进程超时：** 5 分钟无请求后自动关闭
- **端口清理：** 启动时检查并清理僵尸进程

### Claude's Discretion

None specified — all decisions were locked.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PERF-01 | DatabaseRepository with connection pooling replaces scattered sqlite3.connect() calls | Connection pool pattern with Queue; context manager for safe resource management; WAL mode for concurrent access |
| PERF-02 | Streaming import for Excel files with file size validation | openpyxl read_only mode for memory-efficient Excel reading; chunk-based insertion to SQLite |
| PERF-03 | Async geocoding API calls using httpx with retry logic | httpx AsyncClient with connection limits; tenacity async retry with exponential backoff; asyncio.gather for batch processing |
| PERF-04 | Server process cleanup mechanism with PID tracking | PID file management; atexit handlers; timeout-based shutdown; orphan process detection |
| PERF-05 | SQLite WAL mode enabled for better concurrent access | PRAGMA journal_mode=WAL; check_same_thread=False for pool connections; readers don't block writers |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | 0.28.1 | Async HTTP client | Native async/await; HTTP/2 support; unified sync/async API; connection pooling built-in |
| tenacity | 9.1.4 | Retry logic | Async-compatible; exponential backoff; declarative retry configuration |
| pytest-asyncio | 1.3.0 | Async test support | Required for testing async geocoding code |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| respx | 0.22.0 | HTTP mocking for httpx | Mocking Baidu Geocoding API in tests |
| pytest-cov | 7.1.0 | Coverage reporting | Already installed in Phase 1 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| httpx | aiohttp | httpx has better API design and HTTP/2 support; aiohttp requires more boilerplate |
| tenacity | backoff | tenacity has better async support and declarative syntax |
| Queue-based pool | SQLAlchemy pool | SQLAlchemy is overkill for SQLite-only use case; Queue pool is simpler |

**Installation:**
```bash
pip install httpx==0.28.1 tenacity==9.1.4 pytest-asyncio==1.3.0 respx==0.22.0
```

## Architecture Patterns

### Recommended Project Structure
```
.
├── scripts/                  # Existing CLI scripts (modified)
│   ├── chart_generator.py    # Async geocoding
│   ├── data_importer.py      # Streaming Excel import
│   └── server.py             # PID file management
├── database.py               # NEW: DatabaseRepository with connection pooling
├── tests/
│   ├── conftest.py           # Existing fixtures
│   ├── test_database.py      # NEW: Connection pool tests
│   ├── test_async_geocoding.py  # NEW: Async geocoding tests
│   └── test_server_lifecycle.py # NEW: PID management tests
└── outputs/
    └── pids/                 # NEW: PID file storage
```

### Pattern 1: DatabaseRepository with Connection Pooling

**What:** Centralized database access with connection pooling and WAL mode
**When to use:** All database operations throughout the application
**Example:**
```python
# database.py
import sqlite3
import threading
from contextlib import contextmanager
from typing import Iterator, Any
from queue import Queue

class DatabaseRepository:
    """Thread-safe SQLite repository with connection pooling and WAL mode."""

    def __init__(self, db_path: str, pool_size: int = 5):
        self._db_path = db_path
        self._pool: Queue[sqlite3.Connection] = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._initialize_pool(pool_size)

    def _initialize_pool(self, size: int) -> None:
        """Create connection pool with WAL mode enabled."""
        for _ in range(size):
            conn = sqlite3.connect(
                self._db_path,
                check_same_thread=False,  # Required for pool
                timeout=5.0
            )
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for concurrent read/write
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")  # Faster with WAL
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

    def execute_many(self, query: str, params_list: list[tuple]) -> int:
        """Execute many inserts/updates efficiently."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

    def close_all(self) -> None:
        """Close all connections in the pool."""
        while not self._pool.empty():
            conn = self._pool.get()
            conn.close()

# Module-level singleton for backward compatibility
_repo: DatabaseRepository | None = None

def get_repository(db_path: str = "workspace.db") -> DatabaseRepository:
    """Get or create the database repository singleton."""
    global _repo
    if _repo is None:
        _repo = DatabaseRepository(db_path)
    return _repo
```

### Pattern 2: Streaming Excel Import with openpyxl read_only

**What:** Read large Excel files in read-only mode to avoid loading entire workbook into memory
**When to use:** Excel files > 10MB or with many rows
**Example:**
```python
# data_importer.py (additions)
import openpyxl
from typing import Iterator

MAX_EXCEL_SIZE = 100 * 1024 * 1024  # 100MB
STREAMING_CHUNK_SIZE = 10_000  # rows per chunk

def import_excel_streaming(
    file_path: str,
    db_path: str,
    table_name: str,
    repo: DatabaseRepository
) -> Iterator[int]:
    """
    Import Excel file using streaming (read_only mode).
    Yields progress (row count) after each chunk.

    Raises ValueError if file is too large.
    """
    # Validate file size
    file_size = os.path.getsize(file_path)
    if file_size > MAX_EXCEL_SIZE:
        raise ValueError(
            f"Excel 文件过大 ({file_size / 1024 / 1024:.1f}MB)，"
            f"请转换为 CSV 格式后导入（支持超大文件）"
        )

    # Open in read-only mode (streaming)
    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    sheet = wb.active

    # Read header row first
    header = None
    rows_buffer = []
    total_rows = 0

    for row in sheet.iter_rows(values_only=True):
        if header is None:
            # Detect header row (first non-empty row)
            if any(cell is not None for cell in row):
                header = clean_column_names(list(row))
                # Create table with header
                columns_def = ', '.join(f'"{col}" TEXT' for col in header)
                with repo.connection() as conn:
                    conn.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_def})')
                    conn.commit()
            continue

        # Collect rows into buffer
        rows_buffer.append(row)
        total_rows += 1

        # Insert when buffer reaches chunk size
        if len(rows_buffer) >= STREAMING_CHUNK_SIZE:
            _insert_rows_chunk(repo, table_name, header, rows_buffer)
            rows_buffer.clear()
            yield total_rows

    # Insert remaining rows
    if rows_buffer:
        _insert_rows_chunk(repo, table_name, header, rows_buffer)
        yield total_rows

    wb.close()

def _insert_rows_chunk(
    repo: DatabaseRepository,
    table_name: str,
    columns: list[str],
    rows: list[tuple]
) -> None:
    """Insert a chunk of rows efficiently."""
    placeholders = ', '.join('?' * len(columns))
    query = f'INSERT INTO "{table_name}" ({", ".join(f"\"{c}\"" for c in columns)}) VALUES ({placeholders})'
    # Filter out completely null rows
    valid_rows = [row for row in rows if any(cell is not None for cell in row)]
    if valid_rows:
        repo.execute_many(query, valid_rows)
```

### Pattern 3: Async Geocoding with httpx and tenacity

**What:** Concurrent geocoding API calls with retry logic
**When to use:** Batch geocoding (multiple addresses at once)
**Example:**
```python
# chart_generator.py (additions)
import asyncio
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Optional

MAX_CONCURRENT_GEOCODING = 5
GEOCODING_TIMEOUT = 10.0

class AsyncGeocoder:
    """Async geocoding client with caching and retry logic."""

    def __init__(self, ak: str, cache_path: str):
        self._ak = ak
        self._cache_path = cache_path
        self._cache = self._load_cache()

    def _load_cache(self) -> dict:
        try:
            with open(self._cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_cache(self) -> None:
        os.makedirs(os.path.dirname(self._cache_path), exist_ok=True)
        with open(self._cache_path, 'w', encoding='utf-8') as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True
    )
    async def _geocode_single(
        self,
        client: httpx.AsyncClient,
        address: str
    ) -> Optional[list[float]]:
        """Geocode a single address with retry logic."""
        if address in self._cache:
            return self._cache[address]

        url = "https://api.map.baidu.com/geocoding/v3/"
        params = {
            "address": address,
            "output": "json",
            "ak": self._ak
        }

        response = await client.get(url, params=params)
        data = response.json()

        if data.get("status") == 0 and "result" in data:
            loc = data["result"]["location"]
            coord = [loc["lng"], loc["lat"]]
            self._cache[address] = coord
            return coord

        return None

    async def geocode_batch(
        self,
        addresses: list[str]
    ) -> dict[str, Optional[list[float]]]:
        """Geocode multiple addresses concurrently."""
        results: dict[str, Optional[list[float]]] = {}
        uncached = [addr for addr in addresses if addr not in self._cache]

        # Return cached results immediately
        for addr in addresses:
            if addr in self._cache:
                results[addr] = self._cache[addr]

        if not uncached:
            return results

        # Configure connection limits
        limits = httpx.Limits(max_connections=MAX_CONCURRENT_GEOCODING)
        timeout = httpx.Timeout(GEOCODING_TIMEOUT)

        async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_GEOCODING)

            async def bounded_geocode(addr: str) -> tuple[str, Optional[list[float]]]:
                async with semaphore:
                    result = await self._geocode_single(client, addr)
                    return addr, result

            tasks = [bounded_geocode(addr) for addr in uncached]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for item in batch_results:
                if isinstance(item, Exception):
                    logger.error("地理编码请求失败", error=str(item))
                else:
                    addr, coord = item
                    results[addr] = coord

        self._save_cache()
        return results

# Sync wrapper for backward compatibility
def get_geo_coord_batch(addresses: list[str], ak: str, cache_path: str) -> dict:
    """Synchronous wrapper for batch geocoding."""
    geocoder = AsyncGeocoder(ak, cache_path)
    return asyncio.run(geocoder.geocode_batch(addresses))
```

### Pattern 4: Server Process Lifecycle with PID Tracking

**What:** Track server process with PID file, implement timeout shutdown
**When to use:** Server daemon management
**Example:**
```python
# server.py (additions)
import signal
import atexit
from datetime import datetime, timedelta
from pathlib import Path

PID_DIR = Path("outputs/pids")
SERVER_TIMEOUT_MINUTES = 5

class ServerLifecycle:
    """Manage server process lifecycle with PID tracking."""

    def __init__(self, port: int):
        self.port = port
        self.pid_file = PID_DIR / f"server_{port}.pid"
        self.last_request_file = PID_DIR / f"server_{port}_last_request"
        PID_DIR.mkdir(parents=True, exist_ok=True)

    def write_pid(self) -> None:
        """Write current process PID to file."""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

    def read_pid(self) -> int | None:
        """Read PID from file if exists."""
        if not self.pid_file.exists():
            return None
        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, IOError):
            return None

    def clear_pid(self) -> None:
        """Remove PID file."""
        if self.pid_file.exists():
            self.pid_file.unlink()
        if self.last_request_file.exists():
            self.last_request_file.unlink()

    def update_last_request(self) -> None:
        """Update last request timestamp."""
        with open(self.last_request_file, 'w') as f:
            f.write(datetime.now().isoformat())

    def is_server_active(self, pid: int) -> bool:
        """Check if process with PID is running."""
        try:
            os.kill(pid, 0)  # Doesn't actually kill, just checks
            return True
        except (OSError, ProcessLookupError):
            return False

    def kill_orphan(self) -> bool:
        """Kill orphan process if exists and update PID file."""
        pid = self.read_pid()
        if pid and not self.is_server_active(pid):
            # Process is dead but PID file exists
            self.clear_pid()
            return True
        return False

    def should_shutdown(self) -> bool:
        """Check if server should shutdown due to inactivity."""
        if not self.last_request_file.exists():
            return False
        try:
            with open(self.last_request_file, 'r') as f:
                last_request = datetime.fromisoformat(f.read().strip())
            return datetime.now() - last_request > timedelta(minutes=SERVER_TIMEOUT_MINUTES)
        except (ValueError, IOError):
            return False

# Updated server startup
def ensure_server_running() -> str:
    """Ensure server is running, clean up orphans."""
    lifecycle = ServerLifecycle(port=8100)

    # Clean up any orphan processes
    lifecycle.kill_orphan()

    # Check if server already running
    pid = lifecycle.read_pid()
    if pid and lifecycle.is_server_active(pid):
        return f"http://127.0.0.1:{lifecycle.port}"

    # Start new server
    port = find_free_port()
    lifecycle = ServerLifecycle(port)

    # Register cleanup on exit
    atexit.register(lifecycle.clear_pid)

    # Start daemon...
    # (existing daemon startup code)

    return f"http://127.0.0.1:{port}"
```

### Anti-Patterns to Avoid

- **Creating new sqlite3.connect() in each function:** No connection reuse, transaction management issues. Use DatabaseRepository.
- **Loading entire Excel into memory with openpyxl:** Memory overflow for large files. Use read_only mode.
- **Synchronous HTTP calls in loop for geocoding:** Blocking, slow for batch operations. Use async httpx with asyncio.gather.
- **Ignoring server process lifecycle:** Port exhaustion from zombie processes. Track PIDs and implement cleanup.
- **Forgetting WAL mode with connection pool:** "Database is locked" errors. Enable WAL for concurrent access.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Connection pooling | Custom connection manager | Queue-based pool in DatabaseRepository | Thread-safe, context manager, proper cleanup |
| Retry logic | Manual retry loops | tenacity @retry decorator | Exponential backoff, async support, declarative |
| Async HTTP | urllib.request + threading | httpx AsyncClient | Native async, connection pooling, HTTP/2 |
| Process tracking | Manual PID management | ServerLifecycle class | Clean API, atexit cleanup, timeout handling |
| Concurrent execution | Manual thread management | asyncio.gather with Semaphore | Controlled concurrency, clean error handling |

**Key insight:** Python has excellent async and concurrency libraries. Use them instead of building custom solutions.

## Common Pitfalls

### Pitfall 1: Connection Pool Exhaustion

**What goes wrong:** Pool runs out of connections if connections are not returned
**Why it happens:** Exception before `pool.put(conn)` in manual pool management
**How to avoid:** Always use context manager (`with repo.connection() as conn:`)
**Warning signs:** Application hangs on database operations

### Pitfall 2: WAL Mode Not Persisting

**What goes wrong:** PRAGMA journal_mode=WAL is connection-specific, must be set on each connection
**Why it happens:** Setting WAL on one connection doesn't affect others
**How to avoid:** Execute PRAGMA in `_initialize_pool()` for each connection
**Warning signs:** "Database is locked" errors despite pool

### Pitfall 3: openpyxl read_only Mode Limitations

**What goes wrong:** read_only mode cannot handle merged cells, formatting, or formulas
**Why it happens:** read_only streams raw cell values, ignoring workbook structure
**How to avoid:** For files needing merged cell handling, check size first and fall back to standard mode with warning
**Warning signs:** Missing data or wrong values in imported Excel

### Pitfall 4: Async Geocoding Rate Limiting

**What goes wrong:** API returns 429 errors when sending too many concurrent requests
**Why it happens:** Baidu API has QPS limits (default 30 for browser AK, varies for server AK)
**How to avoid:** Use Semaphore to limit concurrency (5 concurrent as per CONTEXT.md decision)
**Warning signs:** Geocoding fails with rate limit errors

### Pitfall 5: PID File Race Condition

**What goes wrong:** Multiple processes try to start server simultaneously
**Why it happens:** PID file check and write is not atomic
**How to avoid:** Use file locking or check process existence after reading PID
**Warning signs:** Multiple server processes running on same port

## Code Examples

### Database Repository Usage (PERF-01, PERF-05)

```python
# Usage in data_importer.py
from database import get_repository

def import_to_sqlite(file_path: str, db_path: str, table_name: str = None) -> list[str]:
    repo = get_repository(db_path)

    # Use context manager for safe connection handling
    with repo.connection() as conn:
        cursor = conn.cursor()
        # ... database operations ...
        conn.commit()

    # Or use high-level methods
    rows = repo.execute_query("SELECT * FROM test_table")
```

### Streaming Excel Import Integration (PERF-02)

```python
# Integration in import_to_sqlite()
def import_to_sqlite(file_path: str, db_path: str, table_name: str = None) -> list[str]:
    # ... existing code ...

    if ext in ['.xlsx', '.xls', '.et']:
        file_size = os.path.getsize(file_path)

        # Use streaming for files > 10MB
        if file_size > 10 * 1024 * 1024:
            logger.info("使用流式导入", file_size_mb=file_size / 1024 / 1024)
            repo = get_repository(db_path)
            for progress in import_excel_streaming(file_path, db_path, table_name, repo):
                logger.debug("导入进度", rows=progress)
        else:
            # Existing logic for smaller files
            # ... unmerge_and_fill_excel ...
```

### Async Geocoding Integration (PERF-03)

```python
# Integration in chart_generator.py
async def generate_chart_async(config: dict) -> str:
    """Async version of chart generation."""
    # ... query data ...

    # Check if geocoding needed
    option_json = json.dumps(config.get("echarts_option", {}))
    if "bmap" in option_json or "geo" in option_json:
        addresses = extract_addresses_from_option(config["echarts_option"])
        if addresses:
            ak = get_baidu_ak()
            cache_path = os.path.join(base_dir, 'references', 'geo_cache.json')
            geocoder = AsyncGeocoder(ak, cache_path)
            coords = await geocoder.geocode_batch(addresses)
            # ... inject coordinates into option ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| sqlite3.connect() per function | DatabaseRepository with pool | Phase 2 | Connection reuse, transaction management |
| Entire Excel in memory | Streaming with read_only | Phase 2 | Handles 100MB+ files |
| urllib.request in loop | httpx AsyncClient + gather | Phase 2 | 5x+ speedup for batch geocoding |
| No server lifecycle | PID tracking + timeout | Phase 2 | No port exhaustion |
| Default journal mode | WAL mode | Phase 2 | Concurrent read/write |

**Deprecated/outdated:**
- Synchronous geocoding with urllib.request: Use async httpx with tenacity retry
- Manual connection management: Use DatabaseRepository singleton

## Open Questions

1. **Streaming Excel merged cells**
   - What we know: read_only mode cannot handle merged cells
   - What's unclear: Should we sacrifice merged cell handling for all large files, or only files above a threshold?
   - Recommendation: Check file size; if < 50MB use existing logic with warning, if > 50MB use streaming with clear limitation message

2. **Repository singleton lifecycle**
   - What we know: Module-level singleton is simple
   - What's unclear: When should the pool be closed?
   - Recommendation: Register atexit handler to close all connections; allow explicit close for testing

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | pyproject.toml (existing) |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ --cov=scripts --cov-fail-under=80 -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PERF-01 | Connection pool provides connections | unit | `pytest tests/test_database.py::test_connection_pool -x` | Wave 0 |
| PERF-01 | Connection returned after context exit | unit | `pytest tests/test_database.py::test_connection_returned -x` | Wave 0 |
| PERF-01 | WAL mode enabled on all connections | unit | `pytest tests/test_database.py::test_wal_mode -x` | Wave 0 |
| PERF-02 | Excel file size validation | unit | `pytest tests/test_data_importer.py::test_excel_size_validation -x` | Wave 0 |
| PERF-02 | Streaming import handles large files | unit | `pytest tests/test_data_importer.py::test_streaming_excel -x` | Wave 0 |
| PERF-02 | Memory usage stays constant | integration | `pytest tests/test_memory.py::test_memory_constant -x` | Wave 0 |
| PERF-03 | Async geocoding with caching | unit | `pytest tests/test_async_geocoding.py::test_geocode_cached -x` | Wave 0 |
| PERF-03 | Retry on transient failure | unit | `pytest tests/test_async_geocoding.py::test_retry_on_failure -x` | Wave 0 |
| PERF-03 | Concurrent requests limited by semaphore | unit | `pytest tests/test_async_geocoding.py::test_concurrency_limit -x` | Wave 0 |
| PERF-04 | PID file created on startup | unit | `pytest tests/test_server_lifecycle.py::test_pid_file_created -x` | Wave 0 |
| PERF-04 | Orphan process detection | unit | `pytest tests/test_server_lifecycle.py::test_orphan_detection -x` | Wave 0 |
| PERF-04 | Timeout shutdown triggers | unit | `pytest tests/test_server_lifecycle.py::test_timeout_shutdown -x` | Wave 0 |
| PERF-05 | Concurrent read/write works | integration | `pytest tests/test_database.py::test_concurrent_access -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q`
- **Per wave merge:** `pytest tests/ --cov=scripts -v`
- **Phase gate:** `pytest tests/ --cov=scripts --cov-fail-under=80 -v`

### Wave 0 Gaps
- [ ] `database.py` - DatabaseRepository with connection pooling and WAL mode
- [ ] `tests/test_database.py` - Connection pool and WAL mode tests
- [ ] `tests/test_async_geocoding.py` - Async geocoding tests with respx mocking
- [ ] `tests/test_server_lifecycle.py` - PID file and process management tests
- [ ] `tests/test_memory.py` - Memory usage validation for large file import
- [ ] Framework install: `pip install httpx tenacity pytest-asyncio respx`

## Sources

### Primary (HIGH confidence)
- .planning/research/STACK.md - Library versions verified from PyPI
- .planning/research/PITFALLS.md - Performance pitfalls identified from codebase audit
- .planning/research/ARCHITECTURE.md - Repository pattern and streaming import patterns
- .planning/phases/01-security-quality-foundation/01-RESEARCH.md - Phase 1 decisions and patterns

### Secondary (MEDIUM confidence)
- openpyxl documentation patterns for read_only mode (training knowledge)
- httpx async client patterns (training knowledge)
- tenacity retry decorator patterns (training knowledge)
- SQLite WAL mode documentation (training knowledge)

### Tertiary (LOW confidence)
- WebSearch for library-specific configurations returned empty; relied on training knowledge

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - versions verified from STACK.md, compatible with existing infrastructure
- Architecture: HIGH - patterns derived from PITFALLS.md and ARCHITECTURE.md research
- Pitfalls: HIGH - identified from existing PITFALLS.md documentation

**Research date:** 2026-04-04
**Valid until:** 30 days (stable libraries, performance patterns are well-established)
