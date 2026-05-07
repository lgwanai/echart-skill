# Feature Research

**Domain:** Data Analysis & Visualization Tools for AI Agents
**Researched:** 2026-04-04
**Confidence:** MEDIUM (Based on project context and domain knowledge; limited external source verification)

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Multi-format data import (CSV, Excel, WPS, Numbers) | Standard interoperability requirement | LOW | Already implemented; users expect seamless file handling |
| SQL query engine | Data analysis requires flexible querying | LOW | SQLite already implemented; table stakes for any analysis tool |
| Basic charts (line, bar, pie, scatter) | Fundamental visualization needs | LOW | Already implemented via ECharts templates |
| Data export (CSV, Excel) | Round-trip data flow is expected | LOW | Already implemented |
| Undo/version control | Users make mistakes; need recovery | MEDIUM | Partially implemented via non-destructive operations |
| Data cleaning (dedupe, fill missing, format standardization) | Real data is always dirty | MEDIUM | Already implemented in data_cleaner.py |
| Chinese map visualization (local) | Local market requirement | MEDIUM | Already implemented with offline map resources |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Dashboard/multi-chart layouts** | Single-view business overview; professional presentation | HIGH | Requires grid system, chart coordination, shared data sources |
| **Gantt chart support** | Project management visualization; timeline planning | MEDIUM | ECharts already supports via custom render; template exists but not exposed as simple API |
| **URL/API data source integration** | Live data feeds; real-time dashboards; eliminate manual file transfer | MEDIUM | Requires HTTP client, auth handling, schema inference, incremental refresh |
| **Team collaboration/sharing** | Multi-user workflows; report distribution; knowledge sharing | HIGH | Conflicts with "local-first, data-never-leaves" core value; needs careful design |
| **AI Agent native design** | Optimized for autonomous agent operation; structured prompts; error recovery | LOW | Already a core differentiator; unique positioning |
| **Business metrics management** | Consistent KPI definitions across analyses; semantic layer | MEDIUM | Already implemented; enhances reproducibility and trust |
| **Semantic data extraction** | AI-powered field extraction, classification, fuzzy matching | MEDIUM | Leverages LLM capabilities beyond traditional tools |
| **100% ECharts 6.0 coverage** | Unmatched chart variety; 40+ chart types including 3D, geo, graphs | LOW | Already implemented; strong differentiator vs basic tools |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Multi-user authentication system | "We need team accounts" | Violates local-first, zero-config promise; adds operational complexity; security surface area | Export/share generated artifacts instead; lightweight token for API data sources |
| Cloud data storage | "Access from anywhere" | Breaks data privacy guarantee; introduces trust issues; compliance complexity | Keep local-first; optional encrypted backup to user-controlled storage |
| External database connectors (MySQL, PostgreSQL) | "Connect to our data warehouse" | Increases complexity; requires drivers, connection strings, network config | Acceptable as future enhancement but not MVP; SQLite provides 80% value with 20% complexity |
| Real-time streaming data | "Live dashboard updates" | WebSocket complexity; state management; resource contention | URL/API data source with scheduled refresh is sufficient for most use cases |
| Mobile-first design | "View on phone" | Charts are complex on small screens; local server architecture doesn't suit mobile | Generate static image exports for mobile viewing; keep desktop-first |
| Complex permission system | "Role-based access control" | Adds friction; contradicts single-user agent design | Simple file-system permissions; agent session isolation |

## Feature Dependencies

```
Dashboard (Multi-chart Layout)
    ├──requires──> Grid Layout Engine
    ├──requires──> Shared Dataset/Filter Coordination
    └──enhances──> Export as Single HTML

Gantt Chart Support
    ├──requires──> Custom ECharts Render Template
    ├──requires──> Time-series Data Structure
    └──enhances──> Project Timeline Visualization

URL/API Data Source
    ├──requires──> HTTP Client with Auth Support
    ├──requires──> Schema Inference for JSON/CSV
    ├──requires──> Incremental Refresh Strategy
    └──conflicts──> Air-gapped Environments

Team Collaboration
    ├──requires──> Report Export Mechanism
    ├──requires──> HTML Dashboard Generation
    ├──conflicts──> Local-first Architecture
    └──enhances──> Knowledge Sharing via Generated Artifacts
```

### Dependency Notes

- **Dashboard requires Grid Layout Engine:** Need coordinate system to position multiple charts in a single view
- **Dashboard requires Shared Dataset/Filter Coordination:** Charts on same dashboard often need linked interactions (filtering one affects others)
- **Gantt Chart requires Custom ECharts Render Template:** ECharts supports Gantt via `custom` series type; existing template proves feasibility
- **URL/API Data Source conflicts with Air-gapped Environments:** Some users work in disconnected environments; must maintain local file primary workflow
- **Team Collaboration conflicts with Local-first Architecture:** Core value is data never leaving local machine; collaboration must focus on sharing results, not data

## MVP Definition

### Launch With (v1 - Already Implemented)

Minimum viable product - what's needed to validate the concept.

- [x] SQLite local data engine - Core architecture
- [x] Multi-format import (CSV, Excel, WPS, Numbers) - File interoperability
- [x] ECharts chart generation (100% template coverage) - Visualization output
- [x] Data cleaning utilities - Handle dirty real-world data
- [x] Metrics management - Semantic layer for consistency
- [x] Chinese province/world offline maps - Local market requirement

### Add After Validation (v1.x - Current Milestone Focus)

Features to add once core is working.

- [ ] **Dashboard/multi-chart layouts** - Requested by power users for comprehensive views
- [ ] **Gantt chart simplified API** - Template exists; need user-friendly interface
- [ ] **URL/API data source** - Eliminates manual file download step
- [ ] **Security fixes** (SQL injection, input validation) - Critical for production trust

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Team collaboration via artifact sharing** - Requires design that preserves local-first principle
- [ ] **External database connectors** - Increases complexity significantly
- [ ] **Streaming/real-time data** - Edge case for current target users
- [ ] **Mobile-responsive chart exports** - Nice-to-have

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Dashboard multi-chart layout | HIGH | MEDIUM | P1 |
| URL/API data source | HIGH | MEDIUM | P1 |
| Gantt chart support | MEDIUM | LOW | P2 |
| Security fixes (SQL injection, validation) | HIGH | LOW | P1 |
| Input validation | HIGH | LOW | P1 |
| Logging framework | MEDIUM | LOW | P2 |
| Team collaboration (artifact sharing) | MEDIUM | HIGH | P3 |
| External database connectors | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for this milestone
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Tableau/Power BI | Jupyter Notebooks | Echart Skill (Current) | Echart Skill (Target) |
|---------|------------------|-------------------|------------------------|----------------------|
| Dashboard layout | Native, drag-drop | Manual matplotlib subplots | Single chart only | Multi-chart grid |
| Data sources | 50+ connectors | Python can read anything | Local files only | Local + URL/API |
| Gantt chart | Built-in | Custom matplotlib | Template exists, not exposed | Simplified API |
| Collaboration | Cloud sharing | Notebook sharing | Not supported | Export artifacts |
| AI integration | Limited | Via extensions | Native agent design | Native agent design |
| Privacy | Cloud-based | Local execution | Local-first (key advantage) | Local-first |
| Setup complexity | Enterprise deployment | Python environment | Zero-config | Zero-config |

## Sources

- Project documentation: `.planning/PROJECT.md` - Validated requirements and scope
- Codebase concerns: `.planning/codebase/CONCERNS.md` - Current gaps and tech debt
- Chart templates: `references/prompts/` directory - 40+ chart types supported
- Gantt example: `references/prompts/dataZoom/gantt_chart_of_airport_flights.md` - Template exists
- Original design doc: `idea.md` - Core scenarios and requirements

---
*Feature research for: Echart Skill data analysis tool*
*Researched: 2026-04-04*
