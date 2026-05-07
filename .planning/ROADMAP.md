# Roadmap: Echart Skill v1.2 高级数据源

## Overview

This milestone adds advanced data source capabilities: external database connections (MySQL, PostgreSQL, MongoDB, SQLite), enhanced HTTP authentication (API Key, OAuth2, additional methods), and scheduled polling with auto-refresh for visualizations. The journey prioritizes database connectivity first (most requested feature), then HTTP enhancements, and finally the polling infrastructure that ties everything together for live data.

## Phases

**Phase Numbering:**
- Phases 1-10: Completed in v1.0 and v1.1
- Phases 11-13: v1.2 milestone work

- [ ] **Phase 11: Database Connections** - Connect to MySQL, PostgreSQL, MongoDB, SQLite
- [ ] **Phase 12: HTTP Enhancements** - API Key, OAuth2, POST/PUT/DELETE
- [ ] **Phase 13: Polling & Auto-Refresh** - Scheduled data refresh with visualization updates

## Phase Details

### Phase 11: Database Connections
**Goal**: Users can connect to external databases and query data for analysis
**Depends on**: Phase 10 (v1.1 complete)
**Requirements**: DB-01, DB-02, DB-03, DB-04, DB-05, DB-06, DB-07
**Success Criteria** (what must be TRUE):
  1. User can connect to MySQL with connection string
  2. User can connect to PostgreSQL with connection string
  3. User can connect to MongoDB with connection string
  4. User can connect to external SQLite file
  5. User can discover tables and schemas
  6. Query results import to DuckDB correctly
  7. Credentials are handled securely (env vars, SecretStr)
**Plans**: 3 plans

Plans:
- [ ] 11-01-PLAN.md - DatabaseConnector base class + SQLAlchemy integration (DB-01, DB-02, DB-04, DB-05)
- [ ] 11-02-PLAN.md - MongoDB connector implementation (DB-03)
- [ ] 11-03-PLAN.md - Schema discovery + metadata tracking + CLI commands (DB-06, DB-07)

### Phase 12: HTTP Enhancements
**Goal**: Users have more authentication options and HTTP methods for API data sources
**Depends on**: Phase 11
**Requirements**: HTTP-01, HTTP-02, HTTP-03, HTTP-04, HTTP-05, HTTP-06
**Success Criteria** (what must be TRUE):
  1. User can authenticate with API Key in header
  2. User can authenticate with API Key in query parameter
  3. User can authenticate with OAuth2 Client Credentials
  4. User can make POST requests with JSON body
  5. User can make PUT requests with JSON body
  6. User can make DELETE requests
  7. Token refresh works automatically for OAuth2
**Plans**: 2 plans

Plans:
- [ ] 12-01-PLAN.md - Enhanced authentication (API Key, OAuth2) (HTTP-01, HTTP-02, HTTP-03)
- [ ] 12-02-PLAN.md - Additional HTTP methods (POST, PUT, DELETE) (HTTP-04, HTTP-05, HTTP-06)

### Phase 13: Polling & Auto-Refresh
**Goal**: Users can schedule automatic data refresh and see live visualizations
**Depends on**: Phase 12
**Requirements**: POLL-01, POLL-02, POLL-03, POLL-04, POLL-05, REFRESH-01, REFRESH-02
**Success Criteria** (what must be TRUE):
  1. User can configure interval polling for HTTP sources
  2. User can configure interval polling for database connections
  3. Polled data updates DuckDB tables automatically
  4. User can trigger manual refresh
  5. Last refresh timestamp is tracked
  6. Charts refresh when data changes
  7. Dashboards refresh when data changes
**Plans**: 2 plans

Plans:
- [ ] 13-01-PLAN.md - Polling infrastructure with APScheduler (POLL-01, POLL-02, POLL-03, POLL-05)
- [ ] 13-02-PLAN.md - Manual refresh + visualization auto-refresh (POLL-04, REFRESH-01, REFRESH-02)

## Progress

**Execution Order:**
Phases execute in numeric order: 11 → 12 → 13

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 11. Database Connections | 3/3 | ✅ Complete | 2026-04-12 |
| 12. HTTP Enhancements | 2/2 | ✅ Complete | 2026-04-12 |
| 13. Polling & Auto-Refresh | 2/2 | ✅ Complete | 2026-04-12 |

### Phase 14: 增加服务启动和关闭指令支持，目前生成的页面需要本地服务才能看到，但是重启电脑后，页面就无法看到了，启动后还需要给出当前能够访问的连接列表

**Goal:** [To be planned]
**Depends on:** Phase 13
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 14 to break down)

---

*Milestone v1.2 COMPLETE - All phases executed successfully.*

*Roadmap defined: 2026-04-12*
*Last updated: 2026-04-12 after milestone completion*
