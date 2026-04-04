# Roadmap: Echart Skill 质量提升与功能扩展

## Overview

This roadmap transforms echart-skill from a functional MVP into a production-ready data analysis toolkit. The journey prioritizes security and quality first (fixing critical SQL injection vulnerabilities and establishing test coverage), then optimizes performance for large-scale data handling, and finally expands features with dashboards, URL data sources, and enhanced chart APIs. Each phase builds on the previous, ensuring stable foundations before feature expansion.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Security & Quality Foundation** - Fix critical vulnerabilities and establish test coverage
- [x] **Phase 2: Performance Optimization** - Optimize for large files and concurrent operations
- [x] **Phase 3: Dashboard Layouts** - Multi-chart dashboard generation with grid layout
- [x] **Phase 4: URL/API Data Source** - Import data from HTTP endpoints with authentication
- [x] **Phase 5: Gantt Chart API** - Simplified Gantt chart wrapper

## Phase Details

### Phase 1: Security & Quality Foundation
**Goal**: Users can trust the system with sensitive data without security risks, and all core workflows are verified by automated tests
**Depends on**: Nothing (first phase)
**Requirements**: SEC-01, SEC-02, SEC-03, SEC-04, QUAL-01, QUAL-02, QUAL-03, QUAL-04, QUAL-05, QUAL-06
**Success Criteria** (what must be TRUE):
  1. SQL injection attempts through table names or file paths are blocked and logged
  2. All exceptions are captured in structured logs visible to users and agents
  3. Baidu API key is loaded from environment variable, not hardcoded
  4. File serving rejects path traversal attempts (e.g., ../../../etc/passwd)
  5. Test suite runs with 80%+ coverage on core modules
**Plans**: 5 plans

Plans:
- [x] 01-01-PLAN.md - Test framework setup + SQL injection fixes (QUAL-03, SEC-01, SEC-02)
- [x] 01-02-PLAN.md - Structured logging infrastructure (QUAL-01, QUAL-02)
- [x] 01-03-PLAN.md - API key migration + Path traversal protection (SEC-03, SEC-04)
- [x] 01-04-PLAN.md - Core module unit tests (QUAL-04)
- [x] 01-05-PLAN.md - Integration tests + Coverage verification (QUAL-05, QUAL-06)

### Phase 2: Performance Optimization
**Goal**: Users can import and process large datasets (100MB+ Excel files) without memory issues or blocking operations
**Depends on**: Phase 1
**Requirements**: PERF-01, PERF-02, PERF-03, PERF-04, PERF-05
**Success Criteria** (what must be TRUE):
  1. Excel files larger than 50MB trigger streaming import instead of in-memory loading
  2. Database queries use connection pooling with automatic cleanup
  3. Geocoding API calls run concurrently with retry logic, not blocking the main thread
  4. Server processes are tracked via PID files and cleaned up on exit
  5. Multiple agents can read the database concurrently without locking
**Plans**: 4 plans

Plans:
- [x] 02-01-PLAN.md - DatabaseRepository with connection pooling and WAL mode (PERF-01, PERF-05)
- [x] 02-02-PLAN.md - Streaming Excel import for large files (PERF-02)
- [x] 02-03-PLAN.md - Async geocoding with httpx and retry logic (PERF-03)
- [x] 02-04-PLAN.md - Server process lifecycle with PID tracking (PERF-04)

### Phase 3: Dashboard Layouts
**Goal**: Users can create multi-chart dashboards with flexible grid layouts in a single HTML file
**Depends on**: Phase 2
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04
**Success Criteria** (what must be TRUE):
  1. User can define dashboard layout with grid configuration (rows, columns, chart positions)
  2. Dashboard configuration is validated against JSON schema before rendering
  3. All charts in dashboard render in a single HTML file that opens in any browser
  4. Dashboard generator script produces valid output from configuration file
**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md - Dashboard configuration schema with pydantic validation (DASH-02)
- [x] 03-02-PLAN.md - Dashboard generator with CSS Grid layout (DASH-01, DASH-03, DASH-04)

### Phase 4: URL/API Data Source
**Goal**: Users can import data from HTTP endpoints (JSON/CSV) with authentication support
**Depends on**: Phase 2
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04
**Success Criteria** (what must be TRUE):
  1. User can import CSV or JSON data from HTTP/HTTPS URL
  2. API endpoints with Basic Auth or Bearer token authentication are supported
  3. JSON response schema is automatically inferred for nested structures
  4. User can manually refresh URL data sources to get updated data
**Plans**: 2 plans

Plans:
- [x] 04-01-PLAN.md - URLDataSource class with authentication support (DATA-01, DATA-02, DATA-03)
- [x] 04-02-PLAN.md - CLI commands and metadata tracking for refresh (DATA-04)

### Phase 5: Gantt Chart API
**Goal**: Users can generate Gantt charts with a simple API without learning ECharts configuration details
**Depends on**: Phase 2
**Requirements**: CHART-01, CHART-02
**Success Criteria** (what must be TRUE):
  1. User can create Gantt chart with task array (name, start, end) input
  2. Gantt chart examples and API documentation are available in SKILL.md
**Plans**: 2 plans

Plans:
- [x] 05-01-PLAN.md - Gantt chart API implementation (CHART-01)
- [x] 05-02-PLAN.md - SKILL.md documentation update (CHART-02)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Security & Quality Foundation | 5/5 | Complete | 01-01, 01-02, 01-03, 01-04, 01-05 |
| 2. Performance Optimization | 4/4 | Complete | 02-01, 02-02, 02-03, 02-04 |
| 3. Dashboard Layouts | 2/2 | Complete | 03-01, 03-02 |
| 4. URL/API Data Source | 2/2 | Complete | 04-01, 04-02 |
| 5. Gantt Chart API | 2/2 | Complete | 05-01, 05-02 |
