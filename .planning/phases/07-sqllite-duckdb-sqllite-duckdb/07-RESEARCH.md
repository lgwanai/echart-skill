# Research: Phase 7 — SQLite → DuckDB Migration

## Phase Goal
将数据导入sqllite的操作换成duckdb，取代sqllite技术方案。充分发挥duckdb优势

## Why DuckDB Over SQLite

| Aspect | SQLite | DuckDB |
|--------|--------|--------|
| Storage model | Row-oriented | Column-oriented (OLAP) |
| Concurrency | WAL mode (concurrent R/W) | Single-writer, multi-reader |
| File format | `.db` / `.sqlite` | `.duckdb` / `.ddb` |
| Analytical queries | Limited (no window functions in older versions) | Full window functions, CTEs, GROUP BY extensions |
| Direct file reading | No (must import first) | Yes (`read_csv_auto()`, `read_parquet()`, `read_json_auto()`) |
| Large dataset performance | Degrades with size | Optimized for GB-scale analytics |
| Python API | `sqlite3` (stdlib) | `duckdb` (pip install) |
| pandas integration | `df.to_sql()` works | `duckdb.register()` + direct SQL on DataFrames |

## Current Architecture Analysis

### Core Files Using SQLite (7 files)

| File | SQLite Usage | Complexity |
|------|-------------|------------|
| `database.py` | `DatabaseRepository` — connection pooling, WAL mode, `sqlite3.connect()` | High — central abstraction |
| `scripts/data_importer.py` | `import sqlite3`, `pd.to_sql()`, `PRAGMA table_info`, `sqlite_master`, `sqlite3.Connection` type hints | High — streaming import, metadata tracking |
| `scripts/data_merger.py` | `import sqlite3`, `sqlite_master` queries | Medium |
| `scripts/data_exporter.py` | Uses `DatabaseRepository` | Low |
| `scripts/chart_generator.py` | Uses `DatabaseRepository` | Low |
| `scripts/dashboard_generator.py` | Uses `DatabaseRepository` | Low |
| `scripts/data_cleaner.py` | Uses `DatabaseRepository`, `sqlite_master` | Low |

### Key Patterns to Migrate

1. **Connection pooling** — SQLite uses queue-based pool with WAL. DuckDB uses single-writer model; connection pooling still useful for concurrent reads but write serialization needed.

2. **Metadata table** — `_data_skill_meta` uses `CREATE TABLE IF NOT EXISTS`, `PRAGMA table_info`, `ALTER TABLE ADD COLUMN`. DuckDB syntax differs:
   - No `PRAGMA table_info` → use `DESCRIBE table_name` or `information_schema.columns`
   - `ALTER TABLE ADD COLUMN` works in DuckDB
   - `CREATE TABLE IF NOT EXISTS` works in DuckDB

3. **Table existence check** — `SELECT name FROM sqlite_master WHERE type='table'` → DuckDB: `SHOW TABLES` or `SELECT table_name FROM information_schema.tables`

4. **Streaming Excel import** — Current approach uses `openpyxl` read-only + chunked `executemany`. DuckDB can use `duckdb.register()` for pandas DataFrames or direct `INSERT INTO ... SELECT` from registered views.

5. **`pd.to_sql()`** — Works with DuckDB via SQLAlchemy or directly via `duckdb` connection. DuckDB's Python API: `conn.execute("INSERT INTO ... SELECT * FROM df")` after `conn.register('df', dataframe)`.

## DuckDB Python API Key Differences

```python
import duckdb

# Connection (no check_same_thread needed)
conn = duckdb.connect('workspace.duckdb')

# Direct SQL on pandas DataFrame
df = pd.read_csv('data.csv')
conn.register('my_data', df)
result = conn.execute("SELECT * FROM my_data WHERE value > 100").fetchdf()

# Read files directly (no import needed!)
result = conn.execute("SELECT * FROM read_csv_auto('data.csv')").fetchdf()
result = conn.execute("SELECT * FROM read_parquet('data.parquet')").fetchdf()
result = conn.execute("SELECT * FROM read_json_auto('data.json')").fetchdf()

# Write to table
conn.execute("CREATE TABLE my_table AS SELECT * FROM my_data")

# Connection settings (replaces PRAGMA)
conn.execute("SET threads=4")
conn.execute("SET memory_limit='2GB'")

# Table info
conn.execute("DESCRIBE my_table").fetchall()
conn.execute("SHOW TABLES").fetchall()
```

## Migration Strategy

### Approach: Abstraction Layer Migration
Replace `database.py` `DatabaseRepository` to wrap DuckDB instead of SQLite. Keep the same public API (`connection()`, `execute_query()`, `execute_many()`) so downstream scripts need minimal changes.

### Key Changes Required
1. **`database.py`**: Rewrite `DatabaseRepository` for DuckDB — remove WAL mode (not applicable), adjust connection pooling for DuckDB's single-writer model
2. **`scripts/data_importer.py`**: Replace `sqlite3` imports, update `PRAGMA` calls, update `sqlite_master` queries, leverage DuckDB's direct file reading for CSV/Excel
3. **`scripts/data_merger.py`**: Update `sqlite_master` → `SHOW TABLES` or `information_schema`
4. **`scripts/data_cleaner.py`**: Update `sqlite_master` queries
5. **`scripts/url_data_source.py`**: Verify compatibility (uses `DatabaseRepository`)
6. **Database file**: Default changes from `workspace.db` → `workspace.duckdb`
7. **SKILL.md**: Update all references from SQLite to DuckDB
8. **README.md**: Update documentation

### Don't Hand-Roll
- Use `duckdb` Python package (pip install duckdb)
- Use `duckdb.register()` for DataFrame → DuckDB table conversion
- Use `read_csv_auto()`, `read_parquet_auto()` for direct file queries
- DuckDB's `INSERT INTO ... SELECT` for bulk inserts (replaces `executemany`)

### Common Pitfalls
- DuckDB's `INTEGER` is 64-bit (SQLite's is variable)
- DuckDB has stricter type checking — `TEXT` columns may need explicit casting
- DuckDB's `BOOLEAN` type vs SQLite's 0/1
- DuckDB doesn't support `PRAGMA` — use `SET` for configuration
- DuckDB's concurrency: single writer, multiple readers — connection pool needs write serialization
- `duckdb.connect()` creates file immediately (unlike SQLite which creates on first write)

### Dependencies
- `duckdb` — pip install (not in current requirements.txt)
- Existing: `pandas`, `openpyxl`, `httpx`, `structlog` — all compatible
