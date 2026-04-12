# Stack Research: Advanced Data Sources (v1.2)

**Date:** 2026-04-12
**Milestone:** v1.2 高级数据源

## Database Connections

### SQLAlchemy (MySQL, PostgreSQL, SQLite)

**Library:** SQLAlchemy 2.0+
**Installation:** `pip install sqlalchemy pymysql psycopg2-binary`

**Why SQLAlchemy:**
- Unified interface for multiple databases
- Connection pooling built-in
- Works well with pandas (`pd.read_sql_query`)
- Mature, well-documented

**Connection Strings:**
```python
# MySQL
engine = create_engine("mysql+pymysql://user:password@host:3306/dbname", pool_recycle=3600)

# PostgreSQL
engine = create_engine("postgresql+psycopg2://user:password@host:5432/dbname")

# SQLite (external file)
engine = create_engine("sqlite:///path/to/database.db")
```

**Integration with DuckDB:**
- Query external DB → pandas DataFrame → write to DuckDB
- No direct bridge needed; use pandas as intermediary

### PyMongo (MongoDB)

**Library:** pymongo 4.16.0+
**Installation:** `pip install pymongo`

**Connection:**
```python
from pymongo import MongoClient

# Standard connection
client = MongoClient("mongodb://user:password@host:27017/dbname")

# Atlas/SRV connection
client = MongoClient("mongodb+srv://user:password@cluster.mongodb.net/dbname")
```

**Query to DataFrame:**
```python
cursor = db.collection.find({"status": "active"})
df = pd.DataFrame(list(cursor))
if "_id" in df.columns:
    df = df.drop(columns=["_id"])
```

## HTTP Enhancements

### Enhanced Authentication

**Library:** httpx-auth
**Installation:** `pip install httpx-auth`

**API Key Patterns:**
```python
from httpx_auth import HeaderApiKey, QueryApiKey

# Header-based (recommended)
auth = HeaderApiKey("YOUR_API_KEY", header_name="X-API-Key")

# Query parameter
auth = QueryApiKey("YOUR_API_KEY", query_parameter_name="api_key")
```

**OAuth2 Client Credentials:**
```python
from httpx_auth import OAuth2ClientCredentials

auth = OAuth2ClientCredentials(
    token_url="https://auth.example.com/token",
    client_id="CLIENT_ID",
    client_secret="CLIENT_SECRET"
)
```

**Custom Auth:**
```python
import httpx

class CustomAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request):
        request.headers["X-Custom-Auth"] = self.token
        yield request
```

### Additional HTTP Methods

Current `URLDataSource` only supports GET. Need to add:
- POST (for API submissions)
- PUT (for updates)
- DELETE (for deletions)

## Polling/Scheduling

### Option 1: APScheduler (Recommended)

**Library:** APScheduler 3.x
**Installation:** `pip install apscheduler`

**Why APScheduler:**
- Async support (AsyncIOScheduler)
- Interval, cron, and date triggers
- Persistent job stores available
- Works well with asyncio

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

async def refresh_data():
    # Fetch new data and update visualizations
    pass

scheduler.add_job(refresh_data, 'interval', seconds=60)
scheduler.start()
```

### Option 2: schedule (Simple)

**Library:** schedule
**Installation:** `pip install schedule`

```python
import schedule
import time

def refresh_data():
    pass

schedule.every(10).minutes.do(refresh_data)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### Option 3: asyncio-based (No extra dependency)

```python
import asyncio

async def poll_data(interval_seconds=60):
    while True:
        await refresh_data()
        await asyncio.sleep(interval_seconds)

asyncio.create_task(poll_data())
```

## Credential Management

**Best Practices:**
1. Use environment variables (never hardcode)
2. Support `.env` file loading
3. Use `SecretStr` in pydantic models
4. Log masked credentials only

```python
import os
from pydantic import SecretStr

db_password = SecretStr(os.environ.get("DB_PASSWORD", ""))
```

## Recommended Additions to requirements.txt

```
# Database connections (Phase 11)
sqlalchemy>=2.0.0
pymysql>=1.1.0
psycopg2-binary>=2.9.0
pymongo>=4.6.0

# Enhanced HTTP auth (Phase 12)
httpx-auth>=0.22.0

# Scheduling (Phase 13)
apscheduler>=3.10.0
```

## What NOT to Add

- **Celery**: Overkill for single-user local tool
- **Django**: We're not building a web framework
- **SQLAlchemy ORM**: Core is sufficient for data extraction
- **Alembic**: No schema migrations needed
