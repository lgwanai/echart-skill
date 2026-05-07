# External Integrations

**Analysis Date:** 2026-04-04

## APIs & External Services

**Baidu Maps API:**
- Purpose: Geocoding addresses to coordinates for map visualizations
- Endpoint: `https://api.map.baidu.com/geocoding/v3/`
- SDK/Client: `urllib.request` (standard library)
- Auth: API Key via `BAIDU_AK` environment variable
- Implementation: `scripts/chart_generator.py` lines 35-67
- Features:
  - Address to coordinate conversion
  - Local caching in `references/geo_cache.json`
  - Fallback handling for browser-type AK limitations

**Baidu Maps JavaScript API:**
- Purpose: Frontend map rendering for `bmap` coordinate system
- Endpoint: `https://api.map.baidu.com/api?v=3.0`
- Auth: Same `BAIDU_AK` as geocoding API
- Implementation: `scripts/chart_generator.py` lines 109-113
- Note: Requires browser-type AK for frontend, server-type for backend geocoding

## Data Storage

**Databases:**
- SQLite 3 (file-based)
  - Default file: `workspace.db`
  - Connection: Standard `sqlite3` Python module
  - Client: `pandas.read_sql_query()` for data extraction
  - Features:
    - `_data_skill_meta` table for import tracking
    - MD5-based duplicate detection
    - Last-used timestamp for cleanup

**File Storage:**
- Local filesystem only
- Input: User-provided CSV/Excel files
- Output: Generated HTML charts, exported CSV/Excel
- Cache: `references/geo_cache.json` for geocoding results

**Caching:**
- Geocoding cache: `references/geo_cache.json`
- In-memory: None (stateless scripts)

## Authentication & Identity

**Auth Provider:**
- None for core functionality
- Optional: Baidu Maps AK for map features
  - No user authentication
  - API key only

## Monitoring & Observability

**Error Tracking:**
- None (console output only)
- Scripts print errors to stdout/stderr

**Logs:**
- No structured logging
- Print statements for user feedback
- HTTP server suppresses access logs (`log_message` overridden)

## CI/CD & Deployment

**Hosting:**
- Local execution only
- No cloud deployment
- HTTP server runs on `127.0.0.1` (localhost only)

**CI Pipeline:**
- None detected

**Distribution:**
- Manual ZIP packaging via `package.sh`
- Excludes: `dist/`, `tmp/`, `outputs/`, `.git/`, `config.txt`

## Environment Configuration

**Required env vars:**
- `BAIDU_AK` - Baidu Maps API Key (optional, only for map charts)

**Secrets location:**
- `config.txt` - User-specific configuration (gitignored)
- `config.example.txt` - Template showing required format

**Configuration precedence:**
1. `config.txt` in project root
2. User prompt (if AK not configured)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- Baidu Geocoding API requests (during chart generation)
- No webhooks or callbacks registered

## Offline Capability

**Fully Offline:**
- Core data processing (SQLite, pandas)
- Static chart generation (ECharts with local maps)
- File import/export

**Requires Internet:**
- Baidu Map geocoding (address to coordinates)
- Baidu Map JavaScript API (for `bmap` coordinate system)
- Fallback: Hardcoded coordinates or local static maps

## Security Considerations

**Data Privacy:**
- All data processing is local
- No data sent to external services except:
  - Address strings for geocoding (Baidu API)
- No cloud storage or analytics

**API Key Handling:**
- Stored in `config.txt` (gitignored)
- Never committed to repository
- Example file shows placeholder only

---

*Integration audit: 2026-04-04*
