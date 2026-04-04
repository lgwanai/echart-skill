# Phase 4: URL/API Data Source - Research

**Researched:** 2026-04-04
**Domain:** HTTP data source import, authentication, schema inference, refresh mechanism
**Confidence:** HIGH (based on existing codebase patterns and established libraries)

## Summary

This phase enables importing data from HTTP/HTTPS endpoints with JSON and CSV support. The codebase already has httpx AsyncClient with tenacity retry logic from Phase 2 (geocoding), a well-established pattern for async HTTP requests. The implementation should extend `data_importer.py` with a new URL import function, create a configuration model using pydantic for authentication (Basic and Bearer token), and add metadata tracking for URL data sources that support refresh. Schema inference for JSON APIs will leverage pandas JSON normalization and pydantic's type inference capabilities.

**Primary recommendation:** Create `URLDataSource` class with httpx AsyncClient for fetching, pydantic models for auth configuration, pandas for CSV/JSON parsing, and extend the existing `_data_skill_meta` table to track URL sources for refresh capability.

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DATA-01 | URL data source import for JSON/CSV from HTTP endpoints | httpx AsyncClient already in use; pandas read_csv/read_json for parsing; streaming support for large responses |
| DATA-02 | Basic auth and Bearer token support for API data sources | httpx Auth classes for Basic Auth; custom headers for Bearer token; pydantic model for auth configuration |
| DATA-03 | Schema inference for JSON API responses | pandas json_normalize for nested structures; pydantic TypeAdapter for schema inference; column name cleaning from existing data_importer |
| DATA-04 | Manual refresh command for URL data sources | Extend _data_skill_meta table with URL tracking; store URL and auth config (encrypted for tokens); CLI refresh command |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | 0.28.1 | Async HTTP client | Already used for geocoding; native async/await; built-in auth support |
| tenacity | 9.1.4 | Retry logic | Already configured; async-compatible; exponential backoff |
| pydantic | 2.12.0 | Auth config validation | Already used for dashboard schema; type-safe configuration |
| pandas | 2.x | CSV/JSON parsing | Already used in data_importer; JSON normalization support |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-asyncio | 1.3.0 | Async test support | Already installed; for testing URL fetch operations |
| respx | 0.22.0 | HTTP mocking | Already installed; for mocking API endpoints in tests |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| httpx | requests | httpx is already integrated with async support; requests is sync-only |
| pydantic for config | dataclasses | pydantic provides validation and serialization; already established pattern |
| pandas for JSON | orjson | pandas handles normalization and type inference; orjson is faster but requires more code |

**Installation:**
No new dependencies required. All libraries already installed from Phase 2.

## Architecture Patterns

### Recommended Project Structure
```
scripts/
├── data_importer.py        # ADD: import_from_url(), refresh_url_source()
├── url_data_source.py      # NEW: URLDataSource class with auth support
└── chart_generator.py      # Existing (httpx pattern reference)
tests/
├── test_url_data_source.py # NEW: URL fetch, auth, schema inference tests
└── conftest.py             # Existing fixtures
```

### Pattern 1: URLDataSource Configuration with Pydantic

**What:** Type-safe configuration for URL data sources with authentication
**When to use:** All URL import operations
**Example:**
```python
# scripts/url_data_source.py
from typing import Literal, Optional
from pydantic import BaseModel, Field, SecretStr, field_validator
import httpx

class BasicAuthConfig(BaseModel):
    """Basic authentication configuration."""
    type: Literal["basic"] = "basic"
    username: str = Field(description="Username for Basic Auth")
    password: SecretStr = Field(description="Password for Basic Auth")

class BearerAuthConfig(BaseModel):
    """Bearer token authentication configuration."""
    type: Literal["bearer"] = "bearer"
    token: SecretStr = Field(description="Bearer token value")

AuthConfig = BasicAuthConfig | BearerAuthConfig | None

class URLDataSourceConfig(BaseModel):
    """Configuration for URL data source import."""
    url: str = Field(description="HTTP/HTTPS URL to fetch data from")
    format: Literal["json", "csv"] = Field(description="Data format")
    auth: Optional[AuthConfig] = Field(default=None, description="Authentication config")
    table_name: str = Field(description="Target table name")
    timeout: float = Field(default=30.0, ge=1.0, le=300.0, description="Request timeout in seconds")

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL is HTTP/HTTPS."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v
```

### Pattern 2: Async HTTP Fetch with Authentication

**What:** Fetch data from URL with optional authentication using httpx
**When to use:** All URL data source imports
**Example:**
```python
# scripts/url_data_source.py
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

MAX_RETRIES = 3
REQUEST_TIMEOUT = 30.0
MAX_RESPONSE_SIZE = 100 * 1024 * 1024  # 100MB

class URLDataSource:
    """Async HTTP data source fetcher with authentication support."""

    def __init__(self, config: URLDataSourceConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    def _build_auth(self) -> Optional[httpx.Auth]:
        """Build httpx auth from configuration."""
        if self.config.auth is None:
            return None

        if isinstance(self.config.auth, BasicAuthConfig):
            return httpx.BasicAuth(
                self.config.auth.username,
                self.config.auth.password.get_secret_value()
            )
        return None  # Bearer handled via headers

    def _build_headers(self) -> dict[str, str]:
        """Build request headers including auth headers."""
        headers = {
            "Accept": "application/json, text/csv, text/plain",
            "User-Agent": "echart-skill/1.0"
        }

        if isinstance(self.config.auth, BearerAuthConfig):
            headers["Authorization"] = f"Bearer {self.config.auth.token.get_secret_value()}"

        return headers

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True
    )
    async def fetch(self) -> str:
        """Fetch data from URL with retry logic.

        Returns:
            Raw response content as string

        Raises:
            httpx.HTTPStatusError: On HTTP errors
            httpx.TimeoutException: On timeout
            ValueError: If response too large
        """
        timeout = httpx.Timeout(self.config.timeout)

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                self.config.url,
                auth=self._build_auth(),
                headers=self._build_headers()
            )
            response.raise_for_status()

            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_RESPONSE_SIZE:
                raise ValueError(f"Response too large: {int(content_length) / 1024 / 1024:.1f}MB > 100MB limit")

            return response.text

    async def fetch_and_parse(self) -> list[dict]:
        """Fetch and parse data from URL.

        Returns:
            List of dictionaries representing rows
        """
        content = await self.fetch()

        if self.config.format == "json":
            return self._parse_json(content)
        else:
            return self._parse_csv(content)
```

### Pattern 3: JSON Schema Inference

**What:** Automatically infer schema from JSON API responses including nested structures
**When to use:** JSON API data imports
**Example:**
```python
# scripts/url_data_source.py
import json
import pandas as pd
from typing import Any

def infer_schema_from_json(data: list[dict] | dict) -> dict[str, str]:
    """Infer column types from JSON data.

    Handles nested structures by flattening with dot notation.
    Returns a mapping of column names to SQLite types.
    """
    # Handle single object response
    if isinstance(data, dict):
        # Check if it's a wrapper with data array
        for key in ['data', 'results', 'items', 'records']:
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
        else:
            data = [data]  # Single record

    if not data:
        return {}

    # Flatten nested structures
    df = pd.json_normalize(data, sep='_')

    # Infer types
    type_map = {
        'int64': 'INTEGER',
        'float64': 'REAL',
        'bool': 'INTEGER',
        'object': 'TEXT',
        'datetime64[ns]': 'TEXT'  # Store as ISO string
    }

    schema = {}
    for col in df.columns:
        pandas_type = str(df[col].dtype)
        schema[col] = type_map.get(pandas_type, 'TEXT')

    return schema

def _parse_json(self, content: str) -> list[dict]:
    """Parse JSON content and flatten nested structures."""
    data = json.loads(content)

    # Auto-detect array location
    if isinstance(data, dict):
        for key in ['data', 'results', 'items', 'records', 'rows']:
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
        else:
            data = [data]

    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}")

    # Flatten nested objects
    df = pd.json_normalize(data, sep='_')

    # Clean column names using existing function
    from data_importer import clean_column_names
    df.columns = clean_column_names(df.columns.tolist())

    return df.to_dict(orient='records')
```

### Pattern 4: URL Data Source Metadata for Refresh

**What:** Track URL sources in metadata table for refresh capability
**When to use:** Recording and refreshing URL imports
**Example:**
```python
# In data_importer.py - extend init_meta_table
def init_meta_table(conn):
    """Initialize metadata table with URL source support."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS _data_skill_meta (
            file_name TEXT,
            table_name TEXT PRIMARY KEY,
            md5_hash TEXT,
            import_time DATETIME,
            last_used_time DATETIME,
            -- URL data source fields
            source_url TEXT,
            source_format TEXT,
            auth_type TEXT,
            last_refresh_time DATETIME
        )
    ''')
    conn.commit()

def record_url_import(
    conn,
    url: str,
    table_name: str,
    source_format: str,
    auth_type: Optional[str] = None
):
    """Record URL data source import for refresh capability."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO _data_skill_meta
        (file_name, table_name, import_time, last_used_time,
         source_url, source_format, auth_type, last_refresh_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (url, table_name, now, now, url, source_format, auth_type, now))
    conn.commit()

def get_url_sources(conn) -> list[dict]:
    """Get all URL data sources for refresh."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT table_name, source_url, source_format, auth_type
        FROM _data_skill_meta
        WHERE source_url IS NOT NULL
    ''')
    return [dict(row) for row in cursor.fetchall()]
```

### Pattern 5: CLI Refresh Command

**What:** Command-line interface for refreshing URL data sources
**When to use:** Manual data refresh operations
**Example:**
```python
# scripts/data_importer.py - add refresh subcommand
import asyncio

async def refresh_url_source(db_path: str, table_name: str) -> bool:
    """Refresh a URL data source.

    Args:
        db_path: Path to SQLite database
        table_name: Name of table to refresh

    Returns:
        True if refresh successful

    Raises:
        ValueError: If table is not a URL data source
    """
    repo = get_repository(db_path)

    with repo.connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT source_url, source_format, auth_type
            FROM _data_skill_meta
            WHERE table_name = ? AND source_url IS NOT NULL
        ''', (table_name,))
        row = cursor.fetchone()

        if not row:
            raise ValueError(f"Table '{table_name}' is not a URL data source")

        config = URLDataSourceConfig(
            url=row['source_url'],
            format=row['source_format'],
            table_name=table_name
        )

        source = URLDataSource(config)
        records = await source.fetch_and_parse()

        # Clear and re-insert
        cursor.execute(f"DELETE FROM {table_name}")
        # ... insert records ...
        conn.commit()

        # Update last_refresh_time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            UPDATE _data_skill_meta
            SET last_refresh_time = ?, last_used_time = ?
            WHERE table_name = ?
        ''', (now, now, table_name))
        conn.commit()

    return True

def list_url_sources(db_path: str) -> list[dict]:
    """List all URL data sources."""
    repo = get_repository(db_path)
    with repo.connection() as conn:
        return get_url_sources(conn)

# CLI integration
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import data from files or URLs")
    subparsers = parser.add_subparsers(dest="command")

    # Existing file import
    file_parser = subparsers.add_parser("file", help="Import from file")
    file_parser.add_argument("input_file")
    file_parser.add_argument("--db", default="workspace.db")
    file_parser.add_argument("--table", default=None)

    # New URL import
    url_parser = subparsers.add_parser("url", help="Import from URL")
    url_parser.add_argument("url", help="HTTP/HTTPS URL")
    url_parser.add_argument("--format", choices=["json", "csv"], required=True)
    url_parser.add_argument("--table", required=True)
    url_parser.add_argument("--db", default="workspace.db")
    url_parser.add_argument("--auth-type", choices=["basic", "bearer"], default=None)
    url_parser.add_argument("--auth-user", help="Username for Basic Auth")
    url_parser.add_argument("--auth-password", help="Password for Basic Auth")
    url_parser.add_argument("--auth-token", help="Token for Bearer Auth")

    # Refresh command
    refresh_parser = subparsers.add_parser("refresh", help="Refresh URL data source")
    refresh_parser.add_argument("table", help="Table name to refresh")
    refresh_parser.add_argument("--db", default="workspace.db")

    # List command
    list_parser = subparsers.add_parser("list", help="List URL data sources")
    list_parser.add_argument("--db", default="workspace.db")
```

### Anti-Patterns to Avoid

- **Storing auth tokens in plain text:** Use SecretStr and consider encryption for persistent storage
- **Blocking HTTP calls in CLI:** Use asyncio.run() for async operations, maintain non-blocking design
- **Assuming JSON array at root:** Check common wrapper keys (data, results, items, records)
- **Ignoring response size limits:** Check Content-Length header before loading large responses
- **Not validating URLs:** Only allow http:// and https:// schemes to prevent SSRF

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP authentication | Custom header manipulation | httpx Auth classes | Built-in support for Basic Auth, tested implementation |
| Bearer token auth | Manual Authorization header | httpx headers dict | Simpler, more maintainable |
| JSON flattening | Recursive dictionary traversal | pandas json_normalize | Handles edge cases, arrays, nested objects |
| Retry logic | Manual retry loops | tenacity decorator | Already configured, async-compatible |
| Secret handling | Plain string storage | pydantic SecretStr | Prevents accidental logging of secrets |

**Key insight:** The codebase already has httpx AsyncClient with tenacity retry from Phase 2. Reuse this pattern for URL data sources.

## Common Pitfalls

### Pitfall 1: JSON Response Structure Assumptions

**What goes wrong:** API responses often wrap data in nested objects
**Why it happens:** Developers assume data is a flat array at root level
**How to avoid:** Check common wrapper keys (data, results, items, records) and auto-detect array location
**Warning signs:** Import shows 0 rows when API returns valid data

### Pitfall 2: Large Response Memory Issues

**What goes wrong:** Loading entire response into memory causes OOM for large APIs
**Why it happens:** No streaming or size validation before parsing
**How to avoid:** Check Content-Length header; use streaming for responses > 10MB
**Warning signs:** Memory errors, slow imports for large datasets

### Pitfall 3: Auth Token Exposure in Logs

**What goes wrong:** Bearer tokens logged in cleartext during debug
**Why it happens:** httpx logs full request headers by default
**How to avoid:** Use pydantic SecretStr for tokens; configure logging to redact Authorization headers
**Warning signs:** Tokens visible in log files

### Pitfall 4: Missing Error Context for API Failures

**What goes wrong:** User sees generic "import failed" without understanding why
**Why it happens:** Not capturing HTTP status codes and response bodies in errors
**How to avoid:** Log status code, response body excerpt, and URL in error messages
**Warning signs:** Users unable to diagnose API configuration issues

### Pitfall 5: Refresh Breaks Foreign Key Relationships

**What goes wrong:** Refreshing a table breaks queries that depend on specific row IDs
**Why it happens:** DELETE + re-insert changes row IDs
**How to avoid:** Document that URL refresh uses full replacement; consider stable ID columns for dependent queries
**Warning signs:** Dashboard queries fail after refresh

## Code Examples

### Complete URL Import Function

```python
# scripts/data_importer.py
import asyncio
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

async def import_from_url(
    url: str,
    db_path: str,
    table_name: str,
    source_format: str,
    auth_config: Optional[AuthConfig] = None
) -> str:
    """Import data from URL into SQLite.

    Args:
        url: HTTP/HTTPS URL to fetch
        db_path: Path to SQLite database
        table_name: Target table name
        source_format: 'json' or 'csv'
        auth_config: Optional authentication configuration

    Returns:
        Name of created table

    Raises:
        ValueError: Invalid URL or format
        httpx.HTTPStatusError: HTTP errors
        httpx.TimeoutException: Request timeout
    """
    from url_data_source import URLDataSource, URLDataSourceConfig

    config = URLDataSourceConfig(
        url=url,
        format=source_format,
        table_name=table_name,
        auth=auth_config
    )

    source = URLDataSource(config)

    logger.info(
        "开始从 URL 导入数据",
        url=url,
        format=source_format,
        table=table_name
    )

    try:
        records = await source.fetch_and_parse()

        if not records:
            logger.warning("URL 返回空数据", url=url)
            raise ValueError("URL returned empty data")

        # Import to SQLite
        repo = get_repository(db_path)
        with repo.connection() as conn:
            # Create table and insert
            df = pd.DataFrame(records)
            df.columns = clean_column_names(df.columns.tolist())
            df.to_sql(table_name, conn, index=False, if_exists='replace')

            # Record import metadata
            auth_type = auth_config.type if auth_config else None
            record_url_import(conn, url, table_name, source_format, auth_type)

        logger.info(
            "URL 数据导入完成",
            table=table_name,
            rows=len(records)
        )

        return table_name

    except Exception as e:
        logger.error(
            "URL 数据导入失败",
            url=url,
            error=str(e),
            error_type=type(e).__name__
        )
        raise

def import_from_url_sync(
    url: str,
    db_path: str = "workspace.db",
    table_name: Optional[str] = None,
    source_format: str = "json",
    auth_config: Optional[AuthConfig] = None
) -> str:
    """Synchronous wrapper for URL import."""
    return asyncio.run(import_from_url(
        url=url,
        db_path=db_path,
        table_name=table_name,
        source_format=source_format,
        auth_config=auth_config
    ))
```

### Test Example for URL Data Source

```python
# tests/test_url_data_source.py
import pytest
import respx
import httpx
from scripts.url_data_source import URLDataSource, URLDataSourceConfig

class TestURLDataSource:
    """Tests for URL data source functionality."""

    @pytest.mark.asyncio
    async def test_fetch_json_no_auth(self):
        """Test fetching JSON without authentication."""
        config = URLDataSourceConfig(
            url="https://api.example.com/data",
            format="json",
            table_name="test_table"
        )

        with respx.mock:
            respx.get("https://api.example.com/data").mock(
                return_value=httpx.Response(200, json={"data": [{"id": 1, "name": "test"}]})
            )

            source = URLDataSource(config)
            records = await source.fetch_and_parse()

        assert len(records) == 1
        assert records[0]["id"] == 1

    @pytest.mark.asyncio
    async def test_fetch_with_bearer_auth(self):
        """Test fetching with Bearer token authentication."""
        from scripts.url_data_source import BearerAuthConfig

        config = URLDataSourceConfig(
            url="https://api.example.com/protected",
            format="json",
            table_name="test_table",
            auth=BearerAuthConfig(token="secret-token")
        )

        with respx.mock as mock:
            # Verify Authorization header is set
            def check_auth(request):
                assert request.headers.get("Authorization") == "Bearer secret-token"
                return httpx.Response(200, json=[{"id": 1}])

            mock.get("https://api.example.com/protected").mock(side_effect=check_auth)

            source = URLDataSource(config)
            await source.fetch_and_parse()

    @pytest.mark.asyncio
    async def test_retry_on_server_error(self):
        """Test retry logic on 5xx errors."""
        config = URLDataSourceConfig(
            url="https://api.example.com/flaky",
            format="json",
            table_name="test_table"
        )

        with respx.mock as mock:
            route = mock.get("https://api.example.com/flaky").mock(
                side_effect=[
                    httpx.Response(500, json={"error": "Internal error"}),
                    httpx.Response(200, json=[{"id": 1}])
                ]
            )

            source = URLDataSource(config)
            records = await source.fetch_and_parse()

        assert route.call_count == 2  # Initial + 1 retry
        assert len(records) == 1

    @pytest.mark.asyncio
    async def test_nested_json_flattening(self):
        """Test that nested JSON structures are flattened."""
        config = URLDataSourceConfig(
            url="https://api.example.com/nested",
            format="json",
            table_name="test_table"
        )

        with respx.mock:
            respx.get("https://api.example.com/nested").mock(
                return_value=httpx.Response(200, json={
                    "data": [
                        {"id": 1, "user": {"name": "Alice", "age": 30}}
                    ]
                })
            )

            source = URLDataSource(config)
            records = await source.fetch_and_parse()

        assert "user_name" in records[0]
        assert records[0]["user_name"] == "Alice"

    @pytest.mark.asyncio
    async def test_response_size_limit(self):
        """Test that large responses are rejected."""
        config = URLDataSourceConfig(
            url="https://api.example.com/large",
            format="json",
            table_name="test_table"
        )

        with respx.mock:
            respx.get("https://api.example.com/large").mock(
                return_value=httpx.Response(
                    200,
                    headers={"content-length": "150000000"},  # 150MB
                    json={}
                )
            )

            source = URLDataSource(config)

            with pytest.raises(ValueError, match="too large"):
                await source.fetch()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| File-only import | URL/API data source support | Phase 4 | Direct API integration without intermediate files |
| Manual curl + file import | Native URL import with auth | Phase 4 | Streamlined workflow, automated refresh |
| Static data | Refreshable URL sources | Phase 4 | Keep data in sync with source APIs |

**Deprecated/outdated:**
- Manual curl to file then import: Use native URL import with authentication
- Copy-paste API responses: Use URL data source with auto-refresh

## Open Questions

1. **Authentication persistence**
   - What we know: Bearer tokens should be stored securely
   - What's unclear: Should tokens be encrypted at rest in the metadata table?
   - Recommendation: Use SecretStr for runtime; consider simple base64 encoding for storage (not cryptographically secure but prevents casual exposure); document that highly sensitive tokens should use environment variables

2. **Streaming support for large CSVs**
   - What we know: pandas read_csv supports chunking
   - What's unclear: Should URL imports support streaming for large CSV files?
   - Recommendation: Yes, add streaming support for Content-Length > 10MB; use httpx.stream() for response and pandas chunk processing

3. **Refresh scheduling**
   - What we know: ADV-03 (scheduled refresh) is deferred to v2
   - What's unclear: Should we add a simple interval-based refresh hint?
   - Recommendation: No, keep it simple for v1; manual refresh is sufficient; scheduling belongs in external automation

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
| DATA-01 | Fetch JSON from URL | unit | `pytest tests/test_url_data_source.py::test_fetch_json_no_auth -x` | Wave 0 |
| DATA-01 | Fetch CSV from URL | unit | `pytest tests/test_url_data_source.py::test_fetch_csv -x` | Wave 0 |
| DATA-01 | Handle HTTP errors | unit | `pytest tests/test_url_data_source.py::test_http_error_handling -x` | Wave 0 |
| DATA-02 | Basic Auth support | unit | `pytest tests/test_url_data_source.py::test_basic_auth -x` | Wave 0 |
| DATA-02 | Bearer token support | unit | `pytest tests/test_url_data_source.py::test_fetch_with_bearer_auth -x` | Wave 0 |
| DATA-03 | JSON schema inference | unit | `pytest tests/test_url_data_source.py::test_nested_json_flattening -x` | Wave 0 |
| DATA-03 | Array detection | unit | `pytest tests/test_url_data_source.py::test_array_detection -x` | Wave 0 |
| DATA-04 | Refresh URL source | unit | `pytest tests/test_url_data_source.py::test_refresh_url_source -x` | Wave 0 |
| DATA-04 | List URL sources | unit | `pytest tests/test_url_data_source.py::test_list_url_sources -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q`
- **Per wave merge:** `pytest tests/ --cov=scripts -v`
- **Phase gate:** `pytest tests/ --cov=scripts --cov-fail-under=80 -v`

### Wave 0 Gaps
- [ ] `scripts/url_data_source.py` - URLDataSource class with auth support
- [ ] `tests/test_url_data_source.py` - URL fetch, auth, schema inference tests
- [ ] Framework install: No new dependencies required (httpx, tenacity, pydantic already installed)

## Sources

### Primary (HIGH confidence)
- scripts/chart_generator.py - AsyncGeocoder pattern for async HTTP with retry
- database.py - DatabaseRepository pattern for connection pooling
- scripts/dashboard_schema.py - Pydantic model patterns with validators
- tests/test_async_geocoding.py - respx mocking patterns for HTTP testing

### Secondary (MEDIUM confidence)
- httpx documentation (training knowledge) - Auth classes, timeout configuration
- pydantic v2 documentation (training knowledge) - SecretStr, field_validator patterns
- pandas documentation (training knowledge) - json_normalize for nested structures

### Tertiary (LOW confidence)
- WebSearch for library-specific patterns returned empty; relied on training knowledge and existing codebase patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all libraries already installed and used in production
- Architecture: HIGH - patterns derived from existing codebase (AsyncGeocoder, DashboardConfig)
- Pitfalls: MEDIUM - based on training knowledge and common HTTP API patterns

**Research date:** 2026-04-04
**Valid until:** 30 days (stable patterns, well-established libraries)
