# Phase 11: Database Connections - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Connect to external databases (MySQL, PostgreSQL, MongoDB, SQLite) and query data for analysis. Query results auto-import to local DuckDB for visualization. Credentials handled securely.

</domain>

<decisions>
## Implementation Decisions

### Connection Config

- **Config format**: JSON config file with connection details
- **Multiple profiles**: One file can contain multiple named connections
- **Credential security**: Support `${ENV_VAR}` placeholders in config, resolve at runtime from environment
- **Config location**: Auto-discover `db_connections.json` in current and parent directories

### Query Interface

- **Primary method**: CLI command for query execution
- **Query source**: Support both inline query string and .sql file path
- **Schema discovery**: Separate commands (list-tables, describe-table, show-schemas)
- **Profile selection**: Explicit `--profile` flag required

### Error Handling

- **Connection failure**: Prompt user to retry or abort
- **Query errors**: Clear error message, exit with code 1
- **Timeout**: Default 30s timeout, configurable via `--timeout` flag
- **Credential errors**: Clear error message with missing credential details

### Output Behavior

- **Result display**: Database-style table (like Excel import output)
- **Integration**: Auto-import to DuckDB, return table name
- **Large results**: Support streaming for large result sets (like existing CSV import)

### Claude's Discretion

- Exact table formatting style (align with existing output patterns)
- Error message wording
- Streaming chunk size for large results
- DuckDB table naming convention (use source table name or generate unique name)

</decisions>

<specifics>
## Specific Ideas

- Output should integrate with existing visualization pipeline (charts, dashboards, Gantt, reports)
- Users familiar with Excel import flow should find database import intuitive
- Config file should be JSON for consistency with other configs in project

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 11-database-connections*
*Context gathered: 2026-04-12*
