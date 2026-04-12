# Features Research: Advanced Data Sources (v1.2)

**Date:** 2026-04-12
**Milestone:** v1.2 高级数据源

## Category 1: Database Connections

### Table Stakes (Must Have)

**DB-01: Connection String Configuration**
- User provides connection string via config file or CLI
- Format: `mysql://user:password@host:port/database`
- Secure handling of credentials (env vars, SecretStr)

**DB-02: Query Execution**
- Execute SQL queries against external databases
- Return results as pandas DataFrame
- Support for large result sets (streaming/chunking)

**DB-03: Schema Discovery**
- List available tables
- Show table structure (columns, types)
- Preview sample data

**DB-04: Data Import to DuckDB**
- Query external DB → DataFrame → save to DuckDB
- Metadata tracking (source, import time, row count)

### Differentiators (Nice to Have)

**DB-05: Connection Pooling**
- Reuse connections for multiple queries
- Configure pool size and timeout

**DB-06: Query History**
- Track executed queries
- Allow re-running previous queries

### Anti-Features (Do NOT Build)

- ORM models for external databases
- Schema migration support
- Write operations to external databases (read-only)

---

## Category 2: HTTP Data Source Enhancements

### Table Stakes (Must Have)

**HTTP-01: API Key Authentication**
- Header-based: `X-API-Key: <key>`
- Query-based: `?api_key=<key>`

**HTTP-02: OAuth2 Client Credentials**
- Token endpoint configuration
- Automatic token refresh

**HTTP-03: Additional HTTP Methods**
- POST with JSON body
- PUT for updates
- DELETE for deletions

**HTTP-04: Request Body Configuration**
- JSON body for POST/PUT
- Form data support

### Differentiators (Nice to Have)

**HTTP-05: Custom Headers**
- User-defined headers per request
- Header templates for common APIs

**HTTP-06: Response Transformation**
- JSONPath to extract nested data
- Custom transformation functions

---

## Category 3: Polling and Auto-Refresh

### Table Stakes (Must Have)

**POLL-01: Interval Polling**
- Configure polling interval (seconds/minutes)
- Fetch data on schedule
- Update local DuckDB table

**POLL-02: Change Detection**
- Compare new data with existing
- Log when data changes detected
- Track last refresh timestamp

**POLL-03: Manual Refresh Trigger**
- CLI command to force immediate refresh
- API endpoint for refresh (if server running)

### Differentiators (Nice to Have)

**POLL-04: Smart Polling**
- Adaptive intervals based on change frequency
- Backoff on errors

**POLL-05: Change Notifications**
- Callback/event on data change
- Integration with visualization refresh

**POLL-06: Polling Status Dashboard**
- Show polling status in CLI
- Last refresh time, next refresh time

### Anti-Features (Do NOT Build)

- Real-time streaming (WebSocket) - Use polling instead
- Push notifications - Local-only tool
- Distributed scheduling - Single-user tool

---

## Category 4: Visualization Refresh Integration

### Table Stakes (Must Have)

**REFRESH-01: Auto-refresh Charts**
- When data changes, update chart data
- Works with existing chart_generator.py

**REFRESH-02: Auto-refresh Dashboards**
- Dashboard components update on data change
- Maintain dashboard state

### Differentiators (Nice to Have)

**REFRESH-03: Browser Auto-refresh**
- Serve HTML with auto-refresh meta tag
- Server-Sent Events for live updates

---

## Feature Complexity Notes

| Feature | Complexity | Dependencies |
|---------|------------|--------------|
| MySQL/PostgreSQL connection | Medium | SQLAlchemy, drivers |
| MongoDB connection | Medium | pymongo |
| SQLite external file | Low | SQLAlchemy |
| API Key auth | Low | httpx-auth |
| OAuth2 client credentials | Medium | httpx-auth |
| POST/PUT/DELETE methods | Low | httpx |
| Interval polling | Medium | APScheduler |
| Change detection | Medium | pandas comparison |
| Visualization refresh | Medium | Integration with existing code |

---

## Dependencies on Existing Features

- **URLDataSource** → Extend with new auth types and methods
- **DuckDB** → Target for all imported data
- **Metadata tracking** → Extend _data_skill_meta for external sources
- **Chart generation** → Needs to support refresh triggers
