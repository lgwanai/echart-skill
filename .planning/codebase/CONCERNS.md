# Codebase Concerns

**Analysis Date:** 2026-04-04

## Tech Debt

### SQL Injection Risk in data_exporter.py
- Issue: Direct string interpolation for table name in SQL query
- Files: `scripts/data_exporter.py:26`
- Code: `df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)`
- Impact: If table_name comes from untrusted input, SQL injection is possible
- Fix approach: Use parameterized queries or validate table names against whitelist

### Silent Exception Handling
- Issue: Multiple bare `except` clauses swallow exceptions silently
- Files:
  - `scripts/chart_generator.py:46` - `except Exception: pass` when loading geo_cache.json
  - `scripts/server.py:41` - `except Exception: pass` when checking server health
  - `scripts/server.py:62` - `except KeyboardInterrupt: pass` (acceptable but logs nothing)
- Impact: Errors are hidden, making debugging difficult
- Fix approach: Log exceptions with `logging` module even if continuing execution

### Hardcoded API Key in config.txt
- Issue: Baidu Map API key is committed in plain text
- Files: `config.txt`
- Impact: Key could be exposed if repo is public; violates security best practices
- Current mitigation: File is in `.gitignore` but key is still in working directory
- Fix approach: Use environment variables or secure secret management; rotate the exposed key

### SQL Injection Risk in data_cleaner.py
- Issue: f-string used for DROP TABLE statement
- Files: `scripts/data_cleaner.py:43`
- Code: `cursor.execute(f"DROP TABLE IF EXISTS {table_name}")`
- Impact: If table_name is manipulated, could drop unintended tables
- Fix approach: Use parameterized queries or validate table names

## Known Bugs

### Numbers Parser Dependency Not in requirements.txt
- Issue: `numbers-parser` package is imported but not listed in requirements
- Files: `scripts/data_importer.py:254`
- Symptoms: ImportError when processing .numbers files if package not manually installed
- Trigger: Import any Mac Numbers file
- Workaround: Manual pip install

### Province Map Name Collision
- Issue: "陕西" (Shaanxi) and "山西" (Shanxi) both map to similar pinyin, causing potential collision
- Files: `scripts/chart_generator.py:136` - uses "shanxi1" for Shaanxi
- Impact: May load wrong map file for one province
- Current mitigation: Hardcoded workaround with "shanxi1"

### Server Port Range Exhaustion
- Issue: Limited port range (8100-8200) with no cleanup of zombie processes
- Files: `scripts/server.py:12-20`
- Trigger: Multiple server starts without proper cleanup
- Impact: "No free ports found" error after ~100 server instances

## Security Considerations

### Local HTTP Server Without Authentication
- Risk: `server.py` runs HTTP server on localhost without any auth
- Files: `scripts/server.py`
- Current mitigation: Only binds to 127.0.0.1
- Recommendations: Add simple token-based auth for production use

### Baidu API Key Exposure in Process List
- Risk: API key visible in process list when server starts
- Files: `scripts/server.py:87`
- Current mitigation: None
- Recommendations: Pass key via environment variable or file descriptor

### Arbitrary File Read via Server
- Risk: CustomHTTPRequestHandler serves files from base directory without path validation
- Files: `scripts/server.py:44-58`
- Current mitigation: Limited to project directory
- Recommendations: Add path traversal protection

### SQL Query Execution Without Validation
- Risk: User-provided queries in data_exporter can execute arbitrary SQL
- Files: `scripts/data_exporter.py:23`
- Current mitigation: SQLite permissions limit damage
- Recommendations: Add query validation or use read-only connections for exports

## Performance Bottlenecks

### Synchronous Geocoding API Calls
- Problem: `get_geo_coord()` makes synchronous HTTP requests
- Files: `scripts/chart_generator.py:35-67`
- Cause: urllib.request blocks while waiting for Baidu API
- Improvement path: Implement batch geocoding or async requests

### Large CSV Loading Without Memory Limits
- Problem: No chunk size limit for Excel files
- Files: `scripts/data_importer.py:238-246`
- Cause: Entire Excel sheet loaded into memory at once
- Improvement path: Add streaming/chunked reading for large files

### No Connection Pooling for SQLite
- Problem: New connection created for every operation
- Files: All scripts using sqlite3
- Cause: `sqlite3.connect()` called in each function
- Improvement path: Implement connection pooling or context manager reuse

## Fragile Areas

### Province Map Detection Logic
- Files: `scripts/chart_generator.py:128-144`
- Why fragile: String matching on JSON content is error-prone
- Safe modification: Use explicit map type parameter instead of string detection
- Test coverage: No automated tests for map injection

### Header Row Detection
- Files: `scripts/data_importer.py:97-108`
- Why fragile: Heuristic-based detection can fail on unusual data layouts
- Safe modification: Allow user to specify header row explicitly
- Test coverage: Limited edge case handling

### Merged Cell Handling in Excel
- Files: `scripts/data_importer.py:110-142`
- Why fragile: Depends on openpyxl internal APIs
- Safe modification: Add fallback for openpyxl version changes
- Test coverage: No tests for complex merged cell scenarios

### Server Process Management
- Files: `scripts/server.py:74-105`
- Why fragile: Daemon process detection relies on health endpoint
- Safe modification: Use PID file or process group management
- Test coverage: No tests for server lifecycle

## Scaling Limits

### SQLite Concurrent Access
- Current capacity: Single-writer, multiple-reader
- Limit: Database locked errors under concurrent writes
- Scaling path: Migrate to PostgreSQL or implement write queue

### Server Port Range
- Current capacity: 100 ports (8100-8200)
- Limit: Exhaustion after many server restarts
- Scaling path: Implement proper process cleanup or use Unix sockets

### File Upload Size
- Current capacity: Limited by available memory
- Limit: Large files (>1GB) will cause memory issues
- Scaling path: Implement streaming imports with progress tracking

## Dependencies at Risk

### numbers-parser (Unlisted Dependency)
- Risk: Not in requirements.txt, optional import
- Impact: .numbers file import fails
- Migration plan: Add to requirements.txt or make optional dependency explicit

### thefuzz (Listed but Unused)
- Risk: Listed in requirements.txt but no usage found
- Impact: Unnecessary dependency
- Migration plan: Remove or implement fuzzy matching features

### matplotlib/seaborn (Listed but Unused)
- Risk: Listed in requirements.txt but chart generation uses ECharts
- Impact: Unnecessary dependency bloat
- Migration plan: Remove if truly unused

## Missing Critical Features

### Input Validation
- Problem: No validation on file paths, table names, or SQL queries
- Blocks: Secure multi-user operation
- Priority: High

### Logging Framework
- Problem: All output uses `print()` statements
- Blocks: Production monitoring and debugging
- Priority: Medium

### Transaction Management
- Problem: No explicit transaction rollback on import failures
- Blocks: Data integrity guarantees
- Priority: High

### Rate Limiting for Geocoding
- Problem: No rate limiting on Baidu API calls
- Blocks: Large dataset geocoding
- Priority: Medium

## Test Coverage Gaps

### Chart Generator
- What's not tested: All chart generation logic
- Files: `scripts/chart_generator.py`
- Risk: HTML generation bugs go unnoticed
- Priority: High

### Data Importer Edge Cases
- What's not tested: Malformed files, encoding issues, large files
- Files: `scripts/data_importer.py`
- Risk: Import failures on real-world data
- Priority: High

### Server Lifecycle
- What's not tested: Port conflicts, daemon management, cleanup
- Files: `scripts/server.py`
- Risk: Resource leaks and port exhaustion
- Priority: Medium

### SQL Query Builder
- What's not tested: Query construction in data_exporter
- Files: `scripts/data_exporter.py`
- Risk: SQL injection or malformed queries
- Priority: High

---

*Concerns audit: 2026-04-04*
