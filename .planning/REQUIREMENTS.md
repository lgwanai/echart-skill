# Requirements: Echart Skill 质量提升与功能扩展

**Defined:** 2026-04-04
**Core Value:** 让数据分析工作人员能够安全、高效地完成从数据导入到可视化输出的全流程，数据绝不出域。

## v1 Requirements

Requirements for this milestone. Each maps to roadmap phases.

### Security

- [x] **SEC-01**: SQL injection vulnerabilities fixed in data_exporter.py and data_cleaner.py using table name whitelist validation
- [x] **SEC-02**: Input validation added for file paths, table names, and SQL queries using pydantic
- [ ] **SEC-03**: Baidu API key removed from config.txt, replaced with environment variable
- [ ] **SEC-04**: Path traversal protection added to server.py file serving

### Quality

- [ ] **QUAL-01**: Logging framework (structlog) replaces all print() statements
- [ ] **QUAL-02**: Silent exception handling eliminated - all exceptions logged
- [x] **QUAL-03**: pytest test framework set up with conftest.py fixtures
- [ ] **QUAL-04**: Unit tests for core modules (chart_generator, data_importer, server)
- [ ] **QUAL-05**: Integration tests for end-to-end workflows
- [ ] **QUAL-06**: Test coverage reaches 80%+ for core modules

### Performance

- [ ] **PERF-01**: DatabaseRepository with connection pooling replaces scattered sqlite3.connect() calls
- [ ] **PERF-02**: Streaming import for Excel files with file size validation
- [ ] **PERF-03**: Async geocoding API calls using httpx with retry logic
- [ ] **PERF-04**: Server process cleanup mechanism with PID tracking
- [ ] **PERF-05**: SQLite WAL mode enabled for better concurrent access

### Dashboard

- [ ] **DASH-01**: Grid layout engine for multi-chart dashboard composition
- [ ] **DASH-02**: Dashboard configuration JSON schema for chart placement
- [ ] **DASH-03**: Single HTML export for complete dashboards
- [ ] **DASH-04**: Dashboard generator script (scripts/dashboard_generator.py)

### Data Source

- [ ] **DATA-01**: URL data source import for JSON/CSV from HTTP endpoints
- [ ] **DATA-02**: Basic auth and Bearer token support for API data sources
- [ ] **DATA-03**: Schema inference for JSON API responses
- [ ] **DATA-04**: Manual refresh command for URL data sources

### Charts

- [ ] **CHART-01**: Gantt chart simplified API wrapper over existing template
- [ ] **CHART-02**: Gantt chart documentation and examples added to SKILL.md

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Collaboration

- **COLLAB-01**: Export dashboard as standalone HTML with embedded data
- **COLLAB-02**: PDF export for dashboards
- **COLLAB-03**: Shareable report generation with embedded charts

### Advanced

- **ADV-01**: External database connectors (MySQL, PostgreSQL)
- **ADV-02**: Real-time streaming data support
- **ADV-03**: Scheduled refresh for URL data sources
- **ADV-04**: Dashboard linked interactions (filter coordination)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Multi-user authentication system | Violates local-first, zero-config promise |
| Cloud data storage | Breaks data privacy guarantee |
| Mobile-first design | Charts are complex on small screens; desktop-first approach |
| Complex permission system | Adds friction; contradicts single-user agent design |
| Real-time WebSocket streaming | URL data source with refresh is sufficient |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SEC-01 | Phase 1 | Complete |
| SEC-02 | Phase 1 | Complete |
| SEC-03 | Phase 1 | Pending |
| SEC-04 | Phase 1 | Pending |
| QUAL-01 | Phase 1 | Pending |
| QUAL-02 | Phase 1 | Pending |
| QUAL-03 | Phase 1 | Complete |
| QUAL-04 | Phase 1 | Pending |
| QUAL-05 | Phase 1 | Pending |
| QUAL-06 | Phase 1 | Pending |
| PERF-01 | Phase 2 | Pending |
| PERF-02 | Phase 2 | Pending |
| PERF-03 | Phase 2 | Pending |
| PERF-04 | Phase 2 | Pending |
| PERF-05 | Phase 2 | Pending |
| DASH-01 | Phase 3 | Pending |
| DASH-02 | Phase 3 | Pending |
| DASH-03 | Phase 3 | Pending |
| DASH-04 | Phase 3 | Pending |
| DATA-01 | Phase 4 | Pending |
| DATA-02 | Phase 4 | Pending |
| DATA-03 | Phase 4 | Pending |
| DATA-04 | Phase 4 | Pending |
| CHART-01 | Phase 5 | Pending |
| CHART-02 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 25
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-04*
*Last updated: 2026-04-04 after roadmap creation*
