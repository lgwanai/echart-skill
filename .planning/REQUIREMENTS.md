# Requirements: Echart Skill v1.1 协作能力

**Defined:** 2026-04-11
**Core Value:** 让数据分析工作人员能够安全、高效地完成从数据导入到可视化输出的全流程，数据绝不出域。

## v1.1 Requirements

Requirements for this milestone. Each maps to roadmap phases.

### HTML Export

- [x] **EXPORT-01**: User can export dashboard as standalone HTML file with all data embedded
- [x] **EXPORT-02**: User can export single chart as standalone HTML file with query data embedded
- [x] **EXPORT-03**: User can export Gantt chart as standalone HTML file with task data embedded
- [x] **EXPORT-04**: Exported HTML files work offline without server or database connection
- [x] **EXPORT-05**: CLI command provides simple interface for export operations

### Data Embedding

- [x] **EMBED-01**: Query results are serialized as JSON and embedded in HTML
- [x] **EMBED-02**: ECharts options are embedded inline in HTML script tag
- [x] **EMBED-03**: Chinese characters are preserved correctly in embedded data (ensure_ascii=False)
- [x] **EMBED-04**: Embedded data size is logged for user awareness

### User Experience

- [x] **UX-01**: Export command accepts output path parameter for file location
- [x] **UX-02**: Exported HTML includes ECharts library from local path (no CDN dependency)
- [x] **UX-03**: Exported HTML filename defaults to chart/dashboard title with timestamp

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### PDF Export

- **PDF-01**: User can export dashboard as PDF file
- **PDF-02**: PDF export supports custom page size and orientation
- **PDF-03**: PDF includes header/footer with metadata

### Advanced Collaboration

- **COLLAB-01**: Shareable report generation with embedded charts and annotations
- **COLLAB-02**: Report templates for common analysis patterns

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| PDF export | Deferred to v1.2, requires additional dependencies |
| Real-time collaboration | Violates local-first principle |
| Cloud sharing | Breaks data privacy guarantee |
| Chart editing in exported HTML | Adds complexity, focus on sharing not editing |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| EXPORT-01 | Phase 9 | Complete |
| EXPORT-02 | Phase 9 | Complete |
| EXPORT-03 | Phase 9 | Complete |
| EXPORT-04 | Phase 9 | Complete |
| EXPORT-05 | Phase 10 | Complete |
| EMBED-01 | Phase 9 | Complete |
| EMBED-02 | Phase 9 | Complete |
| EMBED-03 | Phase 9 | Complete |
| EMBED-04 | Phase 9 | Complete |
| UX-01 | Phase 10 | Complete |
| UX-02 | Phase 10 | Complete |
| UX-03 | Phase 10 | Complete |

**Coverage:**
- v1.1 requirements: 12 total
- Complete: 12 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-11*
*Last updated: 2026-04-12 — Milestone v1.1 complete*
