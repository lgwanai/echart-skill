# Architecture

**Analysis Date:** 2026-04-04

## Pattern Overview

**Overall:** Script-based CLI Tool Architecture with Template-Driven Code Generation

**Key Characteristics:**
- **Local-First Execution**: All data processing happens locally via SQLite and Python scripts
- **Skill/Agent Pattern**: Designed as an AI Agent skill pack with structured operational procedures
- **Template-Driven Visualization**: ECharts configurations generated from 350+ markdown prompt templates
- **Non-Destructive Data Operations**: Creates new tables/views instead of modifying originals (undo mechanism)
- **Offline-First**: Includes all ECharts dependencies locally; no CDN dependencies for core functionality

## Layers

**Data Import Layer:**
- Purpose: Ingest data from various file formats into SQLite
- Location: `scripts/data_importer.py`
- Contains: File parsing, header detection, merged cell handling, MD5 deduplication
- Depends on: pandas, openpyxl, numbers-parser
- Used by: Agent workflows, CLI commands

**Data Storage Layer:**
- Purpose: Local SQLite database with metadata tracking
- Location: `workspace.db` (runtime), `_data_skill_meta` table
- Contains: Imported tables, metadata about imports, usage timestamps
- Depends on: sqlite3
- Used by: All data manipulation scripts

**Data Processing Layer:**
- Purpose: SQL-based querying and Python-based semantic processing
- Location: Agent-generated SQL/Python scripts (runtime)
- Contains: User-defined queries, fuzzy matching, data transformations
- Depends on: SQLite, pandas, thefuzz
- Used by: Agent workflows

**Data Export Layer:**
- Purpose: Export processed data to various formats
- Location: `scripts/data_exporter.py`
- Contains: CSV/Excel export functionality
- Depends on: pandas, sqlite3
- Used by: Agent workflows, CLI commands

**Visualization Layer:**
- Purpose: Generate interactive ECharts HTML visualizations
- Location: `scripts/chart_generator.py`, `scripts/server.py`
- Contains: Chart configuration, HTML generation, local HTTP server
- Depends on: ECharts library (local), Baidu Map API (optional)
- Used by: Agent workflows, CLI commands

**Template/Prompt Layer:**
- Purpose: Provide ECharts configuration templates for 40+ chart types
- Location: `references/prompts/`
- Contains: 350+ markdown files with ECharts option skeletons
- Depends on: None (static assets)
- Used by: Agent to generate chart configurations

**Maintenance Layer:**
- Purpose: Cleanup and metrics management
- Location: `scripts/data_cleaner.py`, `scripts/metrics_manager.py`
- Contains: Old data cleanup, business metric definition storage
- Depends on: sqlite3, datetime
- Used by: Agent workflows, CLI commands

## Data Flow

**File Import Flow:**

1. User provides file (CSV, Excel, WPS .et, Numbers)
2. `scripts/data_importer.py` calculates MD5 hash
3. Check `_data_skill_meta` table for duplicate content
4. If new: Parse file (handle merged cells, detect headers, chunk large files)
5. Clean column names (alphanumeric + underscore only)
6. Write to SQLite table
7. Record import metadata

**Chart Generation Flow:**

1. Agent identifies chart type from user request
2. Read corresponding prompt template from `references/prompts/`
3. Formulate SQL query to aggregate data
4. Generate JSON config with `echarts_option` and `custom_js`
5. `scripts/chart_generator.py` executes query against SQLite
6. Generate HTML with local ECharts dependencies
7. `scripts/server.py` ensures local HTTP server is running
8. Return access URL to user

**Data Export Flow:**

1. User requests export
2. `scripts/data_exporter.py` reads table or executes query
3. Export to CSV (UTF-8 with BOM) or Excel format
4. Save to `outputs/` directory

## Key Abstractions

**Import Metadata Tracking:**
- Purpose: Track file imports and enable deduplication
- Examples: `_data_skill_meta` table in `scripts/data_importer.py`
- Pattern: MD5-based deduplication with timestamp tracking

**Chart Configuration:**
- Purpose: Standardized chart generation interface
- Examples: JSON config structure in `scripts/chart_generator.py`
- Pattern: Declarative configuration with SQL query + ECharts option

**Local HTTP Server:**
- Purpose: Serve generated HTML files with proper CORS
- Examples: `scripts/server.py`
- Pattern: Daemon process with health check endpoint (`/__data_skill_health`)

**Geocoding Cache:**
- Purpose: Cache Baidu Map geocoding results
- Examples: `references/geo_cache.json` in `scripts/chart_generator.py`
- Pattern: File-based JSON cache to minimize API calls

## Entry Points

**CLI Entry Points:**
- `scripts/data_importer.py` - Import files: `python scripts/data_importer.py <file> --db workspace.db`
- `scripts/data_exporter.py` - Export data: `python scripts/data_exporter.py <output> --table <name>`
- `scripts/chart_generator.py` - Generate charts: `python scripts/chart_generator.py --config <json>`
- `scripts/data_cleaner.py` - Cleanup old data: `python scripts/data_cleaner.py --db workspace.db --days 30`
- `scripts/metrics_manager.py` - Add metric definitions: `python scripts/metrics_manager.py --name <name> --desc <desc>`
- `scripts/server.py` - Start HTTP server: `python scripts/server.py`

**Agent Workflow Entry Points:**
- Defined in `SKILL.md` - 8 scenarios with specific procedures
- Triggers: File upload, query request, chart request, export request

## Error Handling

**Strategy:** Explicit error handling with user-friendly messages

**Patterns:**
- Try-catch blocks around file I/O operations
- Validation of required parameters before processing
- Graceful fallbacks (e.g., Excel parsing fallback to pandas)
- Error messages printed to stdout for Agent visibility

## Cross-Cutting Concerns

**Logging:** Console output with structured messages (emojis for visibility in Agent context)

**Validation:**
- File existence checks
- Table name uniqueness enforcement
- SQL query validation via pandas

**Authentication:**
- Baidu Map AK for geocoding (optional, in `config.txt`)
- No other authentication mechanisms

**Data Privacy:**
- All data stays local (SQLite)
- No data sent to external APIs except geocoding (with user consent via AK config)
- MD5 hashing for deduplication (not for security)

---

*Architecture analysis: 2026-04-04*
