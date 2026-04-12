# Phase 11: Database Connections - Research

**Researched:** 2026-04-12
**Status:** Ready for planning

## Summary

Research on implementing external database connections for MySQL, PostgreSQL, MongoDB, and SQLite with secure credential handling, schema discovery, and DuckDB integration.

## Standard Stack

### SQL Database Libraries

**SQLAlchemy Core** (recommended over ORM):
- Why: Efficient for data extraction, no ORM overhead
- Version: 2.0+ with async support
- Patterns: Engine, connection pooling, text() for raw SQL

```python
from sqlalchemy import create_engine, text

# MySQL
engine = create_engine("mysql+pymysql://user:pass@host/db")

# PostgreSQL  
engine = create_engine("postgresql+psycopg2://user:pass@host/db")

# SQLite
engine = create_engine("sqlite:////path/to/file.db")
```

### Database Drivers

**Required packages:**
- `sqlalchemy[asyncio]` - Core library
- `pymysql` - MySQL driver (pure Python, easy install)
- `psycopg2-binary` - PostgreSQL driver (or asyncpg for async)
- `pymongo` - MongoDB driver
- `duckdb` - Already available

### MongoDB Integration

**PyMongo patterns:**
```python
from pymongo import MongoClient

client = MongoClient("mongodb://user:pass@host:port/db")
db = client["database_name"]
collection = db["collection_name"]

# Query and convert to list of dicts
cursor = collection.find({"field": "value"})
records = list(cursor)
```

## Architecture Patterns

### Configuration Management

**JSON config with ENV placeholders:**
```json
{
  "connections": {
    "mysql_prod": {
      "type": "mysql",
      "host": "db.example.com",
      "port": 3306,
      "database": "production",
      "username": "app_user",
      "password": "${MYSQL_PASSWORD}",
      "schema": "public"
    },
    "postgres_analytics": {
      "type": "postgresql",
      "connection_string": "postgresql://user:${PG_PASS}@host/db"
    },
    "mongo_logs": {
      "type": "mongodb",
      "uri": "mongodb://user:${MONGO_PASS}@host:27017/logs"
    }
  }
}
```

**Environment variable resolution:**
```python
import os
import re

def resolve_env_vars(value: str) -> str:
    """Replace ${VAR} with environment variable value."""
    pattern = r'\$\{([^}]+)\}'
    return re.sub(pattern, lambda m: os.getenv(m.group(1), ''), value)
```

### Security Considerations

**From existing patterns (url_data_source.py):**
- Use `SecretStr` from Pydantic for credentials
- Never log sensitive values
- Support multiple auth methods

**New requirements:**
- Validate connection strings before logging
- Support read-only connections (prevent accidental writes)
- Timeout on connections and queries (30s default)

### Schema Discovery

**SQLAlchemy approach:**
```python
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names(schema="public")
columns = inspector.get_columns("table_name")
```

**MongoDB approach:**
```python
# List databases
databases = client.list_database_names()

# List collections
collections = db.list_collection_names()

# Infer schema from sample
sample = collection.find_one()
```

### Data Flow Pattern

**Existing pattern (from data_importer.py):**
1. Validate source
2. Read data in chunks (streaming)
3. Write to DuckDB
4. Track metadata in `_data_skill_meta`

**New database flow:**
1. Load connection config from `db_connections.json`
2. Resolve ENV placeholders
3. Connect with SQLAlchemy or PyMongo
4. Execute query (stream large results)
5. Import to DuckDB with auto table naming
6. Track connection metadata

## CLI Interface Design

**Based on user decisions from CONTEXT.md:**

### Connection Management

```bash
# List available connections
python scripts/db_connector.py list

# Test connection
python scripts/db_connector.py test --profile mysql_prod
```

### Query Execution

```bash
# Inline query
python scripts/db_connector.py query --profile mysql_prod \
  --query "SELECT * FROM users LIMIT 100"

# From file
python scripts/db_connector.py query --profile postgres_analytics \
  --file queries/monthly_sales.sql

# With timeout
python scripts/db_connector.py query --profile mongo_logs \
  --query '{"level": "error"}' --timeout 60
```

### Schema Discovery

```bash
# List tables
python scripts/db_connector.py list-tables --profile mysql_prod

# Describe table
python scripts/db_connector.py describe-table --profile mysql_prod --table users

# Show schemas (PostgreSQL)
python scripts/db_connector.py show-schemas --profile postgres_analytics
```

## Integration Points

### Existing Scripts to Extend

1. **data_importer.py** - Add `db://profile:query` URL scheme
2. **history_viewer.py** - Show database connections in metadata
3. **data_exporter.py** - Support exporting to database (future)

### New Scripts to Create

1. **scripts/db_connector.py** - Main database connection CLI
2. **scripts/db_config.py** - Config loading and validation
3. **scripts/db_schema.py** - Schema discovery utilities

### Metadata Tracking

**Extend `_data_skill_meta` table:**
- `source_type`: "file" | "url" | "database"
- `db_profile`: Connection profile name
- `db_query`: Query executed (truncated)
- `db_host`: Database host (for reference)

## Common Pitfalls

1. **Connection pooling**: SQLAlchemy engines should be reused, not created per query
2. **Large result sets**: Always use server-side cursors or streaming
3. **MongoDB schema**: No fixed schema, need to handle varying fields
4. **Transaction isolation**: Use read-only transactions to prevent writes
5. **Connection timeout**: Set connect timeout separate from query timeout
6. **Driver compatibility**: Test with actual database versions

## Implementation Approach

### Wave 1: Core Infrastructure
- DatabaseConnector base class
- SQLAlchemy implementation (MySQL, PostgreSQL, SQLite)
- Config loading with ENV resolution

### Wave 2: MongoDB + Schema Discovery
- MongoDBConnector implementation
- Schema discovery commands
- Metadata tracking

### Wave 3: Integration + CLI
- CLI commands for query execution
- DuckDB import integration
- Error handling and timeout

## Testing Strategy

**Unit tests:**
- Config validation
- ENV variable resolution
- Query building

**Integration tests:**
- Connect to test databases (Docker containers)
- Execute sample queries
- Verify DuckDB import

**Test databases:**
- Use Docker Compose for MySQL, PostgreSQL, MongoDB
- SQLite: create temp files

## References

- SQLAlchemy 2.0 Documentation: https://docs.sqlalchemy.org/en/20/
- PyMongo Documentation: https://pymongo.readthedocs.io/
- Existing patterns: `scripts/url_data_source.py`, `scripts/data_importer.py`
- Project conventions: Pydantic models, structlog, type annotations

---

*Research completed: 2026-04-12*
*Ready for planning Phase 11*
