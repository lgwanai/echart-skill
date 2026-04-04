# Domain Pitfalls

**Domain:** Python data analysis skill (local-first, SQLite, ECharts visualization)
**Researched:** 2026-04-04
**Confidence:** MEDIUM (project-specific issues from codebase audit; general patterns from training knowledge)

## Critical Pitfalls

### Pitfall 1: SQL Injection via Dynamic Table Names

**What goes wrong:**
String interpolation for table names in SQL queries allows arbitrary SQL execution. The codebase has two confirmed instances:
- `data_exporter.py:26` — `f"SELECT * FROM {table_name}"`
- `data_cleaner.py:43` — `f"DROP TABLE IF EXISTS {table_name}"`

**Why it happens:**
SQLite parameterized queries (`?` placeholders) only work for values, not identifiers (table names, column names). Developers assume parameterization protects all SQL, but it does not cover identifiers.

**How to avoid:**
1. Validate table names against a whitelist of known tables from `sqlite_master`
2. Use identifier quoting with `sqlite3.connect().execute("SELECT quote(?)", (table_name,))` for escaping
3. Implement a validation function:
```python
def validate_table_name(conn, table_name: str) -> str:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    valid_tables = {row[0] for row in cursor.fetchall()}
    if table_name not in valid_tables:
        raise ValueError(f"Invalid table name: {table_name}")
    return table_name
```

**Warning signs:**
- Any f-string or string concatenation in SQL statements
- Table names from user input passed directly to queries
- No validation before executing dynamic DDL/DML

**Phase to address:**
Phase 1 (Security Fixes) — Must be fixed before any feature expansion

---

### Pitfall 2: Silent Exception Swallowing

**What goes wrong:**
Bare `except` clauses with `pass` silently discard errors, making debugging impossible:
- `chart_generator.py:46` — `except Exception: pass` when loading geo_cache.json
- `server.py:41` — `except Exception: pass` when checking server health

**Why it happens:**
Developers add exception handling to "prevent crashes" without considering the value of error information. The intent is graceful degradation, but the result is hidden failures.

**How to avoid:**
1. Always log exceptions before handling:
```python
import logging
logger = logging.getLogger(__name__)

try:
    ...
except Exception as e:
    logger.debug(f"Non-critical error: {e}")
    # Continue with fallback behavior
```
2. Use specific exception types instead of bare `except`
3. Replace `print()` with proper logging throughout

**Warning signs:**
- `except Exception: pass` or `except: pass` in code
- Missing error messages when operations fail
- Inconsistent behavior with no diagnostic trail

**Phase to address:**
Phase 1 (Security Fixes) — Introduce logging framework and fix exception handling

---

### Pitfall 3: Port Exhaustion from Zombie Server Processes

**What goes wrong:**
The server uses a limited port range (8100-8200, 100 ports). Each `ensure_server_running()` spawns a new daemon process without tracking PIDs. No cleanup mechanism exists for crashed or orphaned processes.

**Why it happens:**
The current implementation relies on health checks to detect running servers but has no mechanism to clean up abandoned processes. Process management is delegated to the OS without proper lifecycle tracking.

**How to avoid:**
1. Use PID file to track running server
2. Implement proper shutdown on exit (atexit handler)
3. Add cleanup command to kill orphaned processes:
```python
def cleanup_server():
    pid_file = os.path.join(base_dir, ".server.pid")
    if os.path.exists(pid_file):
        with open(pid_file) as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        os.remove(pid_file)
```

**Warning signs:**
- "No free ports found" error after development iterations
- Multiple `python server.py --daemon` processes in `ps aux`
- Server startup takes progressively longer

**Phase to address:**
Phase 2 (Performance Optimization) — Server process management improvement

---

### Pitfall 4: Memory Overflow from Large File Imports

**What goes wrong:**
While CSV imports use chunking (50k rows), Excel files are loaded entirely into memory with no size limits. The `unmerge_and_fill_excel()` function loads the entire workbook, then creates a DataFrame.

**Why it happens:**
openpyxl requires loading the entire workbook to handle merged cells. Pandas `read_excel` does not support chunked reading natively. Developers assume files are "reasonable size."

**How to avoid:**
1. Check file size before loading:
```python
MAX_EXCEL_SIZE = 100 * 1024 * 1024  # 100MB
if os.path.getsize(file_path) > MAX_EXCEL_SIZE:
    raise ValueError(f"File too large. Use CSV for files > {MAX_EXCEL_SIZE//1024//1024}MB")
```
2. For large files, use `openpyxl` in read-only mode (sacrificing merged cell handling)
3. Add streaming import option with progress tracking

**Warning signs:**
- MemoryError or OOM kills during Excel import
- System becomes unresponsive during import
- Import takes >30 seconds for a single file

**Phase to address:**
Phase 2 (Performance Optimization) — Streaming import implementation

---

### Pitfall 5: Testing Untested Code Without Characterization Tests

**What goes wrong:**
When adding tests to an untested codebase, developers often write tests that reflect "expected" behavior rather than actual behavior. This causes tests to fail when they should pass (test is wrong) or pass when they should fail (code has bugs that tests codify).

**Why it happens:**
Without existing tests, there is no specification of correct behavior. Developers assume they understand the code but miss edge cases and implicit requirements.

**How to avoid:**
1. Write characterization tests first — tests that capture current behavior, bugs and all:
```python
def test_import_csv_current_behavior():
    """Characterization test: captures current behavior, not 'correct' behavior."""
    result = import_to_sqlite("test_data.csv", ":memory:")
    # Assert what actually happens, not what 'should' happen
    assert result == ["test_data"]  # Even if this seems wrong
```
2. Fix bugs in separate commits after characterization tests exist
3. Use `pytest.approx()` for floating point comparisons
4. Mock external dependencies (Baidu API) with `responses` or `pytest-httpserver`

**Warning signs:**
- Tests that require code changes to pass
- Test assertions that describe ideal behavior vs. actual behavior
- Reluctance to run tests during refactoring

**Phase to address:**
Phase 1 (Test Framework) — Establish characterization tests before refactoring

---

### Pitfall 6: Async Conversion Without Understanding Blocking Points

**What goes wrong:**
Converting synchronous code to async without identifying CPU-bound vs I/O-bound operations leads to blocking the event loop. The geocoding API calls (`get_geo_coord`) are I/O-bound and benefit from async, but DataFrame operations in `chart_generator.py` are CPU-bound and will block.

**Why it happens:**
Developers add `async`/`await` keywords without profiling to understand where time is spent. CPU-bound work in async code blocks all coroutines.

**How to avoid:**
1. Profile before converting:
```python
import cProfile
cProfile.run('generate_chart(config)')
```
2. For CPU-bound work (DataFrame operations), use `run_in_executor`:
```python
async def generate_chart_async(config):
    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(None, lambda: pd.read_sql_query(query, conn))
```
3. For I/O-bound work (API calls), use `aiohttp`:
```python
async def get_geo_coord_async(address, ak):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            ...
```

**Warning signs:**
- "Async" code that shows no performance improvement
- One slow operation blocking all concurrent requests
- High CPU usage while waiting for I/O

**Phase to address:**
Phase 2 (Performance Optimization) — Async geocoding with proper separation of concerns

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `print()` for output | No dependencies, simple | No log levels, no timestamps, cannot filter | Never in production code |
| Bare `except: pass` | Prevents crashes | Hides bugs, impossible to debug | Never |
| Hardcoded API keys in config | Works immediately | Security exposure, key rotation difficult | Only in `.gitignore`d files, rotate immediately |
| No connection pooling | Simpler code | Connection overhead on every operation | Never for SQLite — use context managers |
| F-string SQL | Dynamic queries | SQL injection risk | Never |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Baidu Geocoding API | Synchronous calls in loop | Batch geocoding with rate limiting (max 30 QPS) |
| ECharts map loading | String detection for province names | Explicit map type parameter with validation |
| SQLite database | New connection per function | Connection pool or context manager reuse |
| Local file imports | No size validation | Check file size before loading into memory |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading entire Excel to memory | MemoryError, OOM kill | Stream CSV, limit Excel size | Files >100MB |
| Synchronous geocoding loop | Hours for 1000 locations | Batch API, caching, async | >100 locations |
| SQLite concurrent writes | "Database is locked" errors | Write queue or migrate to PostgreSQL | >5 concurrent writers |
| Server port exhaustion | "No free ports found" | PID tracking, cleanup on exit | >100 server restarts |
| No connection reuse | Slow query execution | Connection pool/context manager | >100 queries/operation |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| F-string SQL with table names | Data exfiltration, data loss | Whitelist table names from sqlite_master |
| API key in process list | Key exposure to other users | Pass via environment variable |
| Local HTTP server no auth | Local attacks if port exposed | Token-based auth, bind to 127.0.0.1 only |
| Path traversal in file handler | Arbitrary file read | Validate paths stay within base directory |
| No input validation on imports | Malformed file DoS | Validate file size, structure before processing |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Silent failures | "It just doesn't work" with no guidance | Return error messages with actionable suggestions |
| No progress indication for large imports | User thinks process is hung | Progress bar or percentage updates |
| Hardcoded error messages in Chinese | Non-Chinese users confused | Localization or English defaults |
| No feedback on duplicate import | User confused why import "skipped" | Clear message: "Already imported as table X" |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Chart generation works:** Often missing error handling for empty DataFrames — verify with empty query results
- [ ] **Import completes:** Often missing validation that tables are readable — verify with `SELECT COUNT(*)`
- [ ] **Server starts:** Often missing health check verification — verify `curl localhost:port/__data_skill_health`
- [ ] **Tests pass:** Often missing edge case tests (empty files, special characters, large files) — verify with boundary test cases
- [ ] **Logging added:** Often missing log level configuration — verify logs appear at correct levels

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| SQL injection vulnerability | HIGH | Audit all SQL, add parameterization, rotate credentials |
| Silent exception swallowing | MEDIUM | Add logging, reproduce failures from logs |
| Port exhaustion | LOW | Kill orphan processes, add PID tracking |
| Memory overflow | MEDIUM | Add file size checks, implement streaming |
| Untested code | HIGH | Write characterization tests, fix bugs incrementally |
| Async blocking | MEDIUM | Profile, separate I/O from CPU, use executors |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| SQL injection | Phase 1 (Security) | Security scan with `bandit`, manual code review |
| Silent exceptions | Phase 1 (Security) | Code review for bare except, logging audit |
| Port exhaustion | Phase 2 (Performance) | Test server restart 100+ times |
| Memory overflow | Phase 2 (Performance) | Test with 500MB+ files |
| Testing untested code | Phase 1 (Testing) | Characterization tests pass before any refactoring |
| Async blocking | Phase 2 (Performance) | Profile async version vs sync, verify no regression |

## Sources

- Project codebase audit: `.planning/codebase/CONCERNS.md`
- Python sqlite3 documentation (parameterization limitations for identifiers)
- "Working Effectively with Legacy Code" by Michael Feathers (characterization testing)
- Python asyncio documentation (blocking event loop, run_in_executor)
- ECharts documentation (map loading, dashboard layout)
- pandas documentation (chunked reading, memory optimization)

---
*Pitfalls research for: Python data analysis skill*
*Researched: 2026-04-04*
