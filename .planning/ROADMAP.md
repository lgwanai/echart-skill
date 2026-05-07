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

### Phase 14: 服务启动和关闭指令支持
**Goal**: Add /start, /stop, /status commands to manage local HTTP server for viewing generated charts, with link list display after service starts
**Depends on**: Phase 13
**Requirements**: SRV-01, SRV-02, SRV-03, SRV-04, SRV-05
**Success Criteria** (what must be TRUE):
  1. User can start local HTTP server with /start command
  2. User can stop server with /stop command
  3. User can check service status with /status command
  4. Service state persists to outputs/.server_status.json
  5. Server starts on available port (8100-8200)
  6. User sees list of accessible chart URLs after starting server
  7. Status shows file names with creation times and full URLs
**Plans**: 2 plans

Plans:
- [ ] 14-01-PLAN.md - Server management CLI with /start, /stop, /status commands (SRV-01, SRV-02, SRV-03, SRV-04)

### Phase 15: 地图生成优化与测试验证
**Goal**: Fix map chart generation issues, optimize prompts to use local static maps correctly, add comprehensive test validation
**Depends on**: Phase 14
**Requirements**: MAP-01, MAP-02, MAP-03, MAP-04, MAP-05
**Success Criteria** (what must be TRUE):
  1. All map prompt templates explicitly instruct to use local static maps (china.js, world.js) WITHOUT $.get or registerMap
  2. SKILL.md contains clear Map Generation Priority rules with examples
  3. Test suite validates China map, World map, Province map, BMap mode correctly
  4. All map chart tests pass (test_china_static_map, test_world_static_map, test_bmap_mode_with_baidu_ak)
  5. Documentation exists for map chart best practices (docs/map_chart_best_practices.md)
  6. New prompt templates created for china_static_map.md and world_static_map.md
**Plans**: 1 plan

Plans:
- [x] 15-01-PLAN.md - Map generation optimization: update SKILL.md, create test suite, add new prompt templates, create best practices documentation (MAP-01, MAP-02, MAP-03, MAP-04, MAP-05)

### Phase 16: Dashboard专业仪表盘支持
**Goal**: Add professional dashboard generation with modern UI/UX, interactive features, and responsive design
**Depends on**: Phase 15
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06
**Success Criteria** (what must be TRUE):
  1. Users can generate multi-chart dashboards with /dashboard command
  2. Dashboard uses professional card-based layout with CSS Grid
  3. Dark/Light theme toggle works correctly
  4. Dashboard is fully responsive (mobile, tablet, desktop)
  5. Users can export dashboard as PDF
  6. Charts support auto-refresh, search filtering, and individual download
  7. Dashboard assets (CSS/JS) are properly loaded from assets/dashboard/
  8. Example dashboard configuration exists (examples/dashboard_config.json)
**Plans**: 1 plan

Plans:
- [x] 16-01-PLAN.md - Dashboard generation: create professional UI template, update dashboard_generator.py, add /dashboard command to SKILL.md, create example config (DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06)
- [ ] 14-02-PLAN.md - Status reporting and chart link listing utility (SRV-05)

---

*Milestone v1.2 COMPLETE - All phases executed successfully.*

*Roadmap defined: 2026-04-12*
*Last updated: 2026-04-12 after milestone completion*
