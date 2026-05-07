# Requirements: Echart Skill v1.2 高级数据源

**Defined:** 2026-04-12
**Core Value:** 让数据分析工作人员能够安全、高效地完成从数据导入到可视化输出的全流程，数据绝不出域。

## v1.2 Requirements

Requirements for this milestone. Each maps to roadmap phases.

### Database Connections

- [x] **DB-01**: User can connect to MySQL database with connection string
- [x] **DB-02**: User can connect to PostgreSQL database with connection string
- [x] **DB-03**: User can connect to MongoDB database with connection string
- [x] **DB-04**: User can connect to external SQLite database file
- [x] **DB-05**: User can execute SQL queries against external databases
- [x] **DB-06**: User can discover tables and schemas in external databases
- [x] **DB-07**: Query results from external databases can be imported to DuckDB

### HTTP Enhancements

- [x] **HTTP-01**: User can authenticate with API Key in header
- [x] **HTTP-02**: User can authenticate with API Key in query parameter
- [x] **HTTP-03**: User can authenticate with OAuth2 Client Credentials flow
- [x] **HTTP-04**: User can make POST requests with JSON body
- [x] **HTTP-05**: User can make PUT requests with JSON body
- [x] **HTTP-06**: User can make DELETE requests

### Polling

- [x] **POLL-01**: User can configure interval polling for HTTP data sources
- [x] **POLL-02**: User can configure interval polling for database connections
- [x] **POLL-03**: Polling automatically updates local DuckDB tables
- [x] **POLL-04**: User can trigger manual refresh of data sources
- [x] **POLL-05**: Polling tracks last refresh timestamp

### Visualization Refresh

- [x] **REFRESH-01**: Charts auto-refresh when polled data changes
- [x] **REFRESH-02**: Dashboards auto-refresh when polled data changes

### Server Management

- [ ] **SRV-01**: User can start local HTTP server with /start command (aliases: /server, /启动服务)
- [ ] **SRV-02**: User can stop server with /stop command (alias: /停止服务)
- [ ] **SRV-03**: User can check service status with /status command (alias: /状态)
- [ ] **SRV-04**: Service state persists to outputs/.server_status.json (PID, port, start time)
- [x] **SRV-05**: User sees list of accessible chart URLs after starting server (with file metadata)

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Cloud Data Sources

- **CLOUD-01**: User can connect to AWS S3 buckets
- **CLOUD-02**: User can connect to Google Cloud Storage
- **CLOUD-03**: User can connect to Azure Blob Storage

### Advanced Polling

- **POLL-ADV-01**: Smart polling with adaptive intervals
- **POLL-ADV-02**: Change notifications via webhook

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Write operations to external databases | Read-only access, local-first principle |
| Real-time streaming (WebSocket) | Polling sufficient for data analysis use case |
| Cloud database services (RDS, Cloud SQL) | Focus on self-hosted databases first |
| ORM models for external databases | SQLAlchemy Core sufficient for data extraction |
| Celery task queue | Overkill for single-user local tool |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DB-01 | Phase 11 | ✅ Complete |
| DB-02 | Phase 11 | ✅ Complete |
| DB-03 | Phase 11 | ✅ Complete |
| DB-04 | Phase 11 | ✅ Complete |
| DB-05 | Phase 11 | ✅ Complete |
| DB-06 | Phase 11 | ✅ Complete |
| DB-07 | Phase 11 | ✅ Complete |
| HTTP-01 | Phase 12 | ✅ Complete |
| HTTP-02 | Phase 12 | ✅ Complete |
| HTTP-03 | Phase 12 | ✅ Complete |
| HTTP-04 | Phase 12 | ✅ Complete |
| HTTP-05 | Phase 12 | ✅ Complete |
| HTTP-06 | Phase 12 | ✅ Complete |
| POLL-01 | Phase 13 | ✅ Complete |
| POLL-02 | Phase 13 | ✅ Complete |
| POLL-03 | Phase 13 | ✅ Complete |
| POLL-04 | Phase 13 | ✅ Complete |
| POLL-05 | Phase 13 | ✅ Complete |
| REFRESH-01 | Phase 13 | ✅ Complete |
| REFRESH-02 | Phase 13 | ✅ Complete |
| SRV-01 | Phase 14 | ⏳ Planned |
| SRV-02 | Phase 14 | ⏳ Planned |
| SRV-03 | Phase 14 | ⏳ Planned |
| SRV-04 | Phase 14 | ⏳ Planned |
| SRV-05 | Phase 14 | ⏳ Planned |

**Coverage:**
- v1.2 requirements: 20 total
- Mapped to phases: 20
- Complete: 20/20 ✓
- Phase 14 requirements: 5 total
- Mapped to phases: 5
- Complete: 0/5 (planned)

---

*Requirements defined: 2026-04-12*
*Last updated: 2026-04-12 after v1.2 milestone completion*
