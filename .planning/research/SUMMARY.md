# Project Research Summary

**Project:** echart-skill
**Domain:** Python data analysis tool (local-first, agent skill pack with ECharts visualization)
**Researched:** 2026-04-04
**Confidence:** MEDIUM-HIGH

## Executive Summary

This is a local-first Python data analysis tool designed as an AI agent skill pack, featuring SQLite-based data management and ECharts visualization. The product follows a unique "agent-native" design philosophy where AI agents orchestrate data workflows rather than human users directly. Research reveals a solid MVP foundation (multi-format import, SQL engine, 100% ECharts 6.0 chart coverage) but critical security vulnerabilities (SQL injection via dynamic table names) and untested code that must be addressed before feature expansion.

The recommended approach prioritizes security fixes and test infrastructure in Phase 1, followed by performance optimization (streaming imports, async geocoding) and then feature expansion (dashboard layouts, URL data sources). This ordering is critical: adding features to an untested, insecure codebase will amplify technical debt exponentially. The architecture should evolve toward a Repository pattern for database access and async I/O for external API calls, while preserving the local-first, zero-config promise that differentiates this tool from cloud-based alternatives.

Key risks include SQL injection vulnerabilities in dynamic table name handling, silent exception swallowing that hinders debugging, and potential memory overflow on large Excel file imports. Mitigation requires immediate security fixes, structured logging implementation, and streaming import patterns.

## Key Findings

### Recommended Stack

The project uses Python 3.13+ with a focused set of dependencies optimized for data analysis and AI agent integration. pytest with pytest-asyncio provides the testing foundation, structlog delivers structured logging for AI agent consumption, and httpx with respx handles async HTTP operations and mocking. pydantic enforces input validation at system boundaries, addressing the zero-trust requirement.

**Core technologies:**
- pytest 9.0.2: Testing framework with native async support and marker-based test categorization
- structlog 25.5.0: Structured logging optimized for AI agent consumption with context binding
- httpx 0.28.1: Modern async HTTP client with HTTP/2 support, replacing sync-only requests
- pydantic 2.12.5: Runtime validation with type hints for zero-trust boundary enforcement
- tenacity 9.1.4: Async-compatible retry logic for geocoding API resilience

**Development tools:**
- ruff 0.15.9: Unified linting and formatting (replaces flake8 + isort + black)
- mypy 1.20.0: Static type checking with strict mode

### Expected Features

The MVP is largely complete with SQLite local data engine, multi-format import (CSV, Excel, WPS, Numbers), ECharts chart generation with 100% template coverage, data cleaning utilities, metrics management, and offline Chinese/world maps.

**Must have (table stakes - already implemented):**
- Multi-format data import (CSV, Excel, WPS, Numbers) - Standard interoperability
- SQL query engine via SQLite - Flexible data analysis
- Basic charts (line, bar, pie, scatter) - Fundamental visualization
- Data export (CSV, Excel) - Round-trip data flow
- Chinese map visualization (local) - Local market requirement

**Should have (competitive - current milestone focus):**
- Dashboard/multi-chart layouts - HIGH user value, professional presentation
- URL/API data source integration - Eliminates manual file transfer
- Security fixes (SQL injection, input validation) - Critical for production trust
- Gantt chart simplified API - Template exists, needs user-friendly interface

**Defer (v2+):**
- Team collaboration via artifact sharing - Must preserve local-first principle
- External database connectors (MySQL, PostgreSQL) - Increases complexity significantly
- Real-time streaming data - Edge case for current target users

### Architecture Approach

The current architecture uses direct sqlite3 connections scattered across functions, synchronous HTTP for geocoding API calls, and in-memory file loading. The recommended evolution introduces a Repository pattern for database abstraction with connection pooling, streaming imports for large files, and async HTTP client for concurrent geocoding API calls.

**Major components:**
1. DatabaseRepository - Abstracts all SQLite operations with connection pooling and parameterized queries
2. DataImporter - Streaming file imports with chunked processing for memory safety
3. ChartGenerator - ECharts HTML generation with async geocoding for map charts
4. Server - aiohttp-based local HTTP server for serving chart files

**Key patterns:**
- Repository pattern for testability and connection management
- Streaming imports (pandas chunksize) for constant memory usage
- Async batch geocoding with caching for performance
- pytest fixtures for test isolation

### Critical Pitfalls

1. **SQL Injection via Dynamic Table Names** - SQLite parameterization does not protect identifiers. Validate table names against sqlite_master whitelist before using in SQL. Phase 1 critical fix.

2. **Silent Exception Swallowing** - Bare `except: pass` clauses hide failures. Replace with structlog logging and specific exception types. Phase 1 critical fix.

3. **Port Exhaustion from Zombie Server Processes** - No PID tracking for daemon processes. Implement PID file tracking and atexit cleanup. Phase 2 fix.

4. **Memory Overflow from Large Excel Imports** - Excel files loaded entirely into memory. Add file size limits and streaming CSV preference. Phase 2 fix.

5. **Testing Untested Code Without Characterization Tests** - Writing tests that assume "correct" behavior rather than capturing actual behavior. Write characterization tests first before any refactoring. Phase 1 requirement.

## Implications for Roadmap

Based on combined research, suggested phase structure:

### Phase 1: Security & Test Foundation
**Rationale:** Critical security vulnerabilities and absent test coverage block safe feature development. SQL injection risks data loss; untested code makes refactoring dangerous. Must establish safety net before expansion.
**Delivers:** Secure database operations, structured logging, comprehensive test suite with 80%+ coverage
**Addresses:** Security fixes from FEATURES.md (P1)
**Avoids:** SQL injection, silent exception swallowing from PITFALLS.md; testing untested code pitfall
**Uses:** pytest, structlog, pydantic from STACK.md

### Phase 2: Performance Optimization
**Rationale:** With tests in place, safe to refactor for performance. Large file handling and slow geocoding are user-facing pain points that become worse with feature expansion.
**Delivers:** Streaming imports for large files, async batch geocoding with caching, connection pooling
**Uses:** httpx async client, tenacity retry, pandas chunksize from STACK.md
**Implements:** DatabaseRepository from ARCHITECTURE.md; AsyncGeocoder pattern
**Avoids:** Memory overflow, port exhaustion, async blocking from PITFALLS.md

### Phase 3: Dashboard & Multi-Chart Layouts
**Rationale:** Most requested feature (HIGH user value). Pure ECharts grid implementation - no new Python dependencies. Requires stable foundation from Phases 1-2.
**Delivers:** Multi-chart dashboard generation with grid layout
**Addresses:** Dashboard feature from FEATURES.md (P1)
**Uses:** ECharts grid option (no new stack dependencies)

### Phase 4: URL/API Data Source
**Rationale:** Eliminates manual file download step. Requires HTTP client infrastructure from Phase 2. Introduces external integration complexity.
**Delivers:** URL and API endpoint as data sources with schema inference
**Addresses:** URL/API data source from FEATURES.md (P1)
**Uses:** httpx, pydantic validation from STACK.md
**Avoids:** Input validation gaps from PITFALLS.md

### Phase 5: Gantt Chart API
**Rationale:** Template already exists, needs user-friendly API wrapper. LOW implementation cost relative to value.
**Delivers:** Simplified Gantt chart API
**Addresses:** Gantt chart from FEATURES.md (P2)

### Phase Ordering Rationale

- Phase 1 must come first because adding features to insecure, untested code amplifies technical debt exponentially
- Phase 2 before Phase 3-5 because performance issues become more acute with feature complexity
- Phases 3-4 are P1 features from FEATURES.md; Phase 5 is P2
- Repository pattern (Phase 1) enables testability for all subsequent phases
- Async infrastructure (Phase 2) required for URL/API data source (Phase 4)

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4:** Complex integration with external APIs; needs research on auth patterns, rate limiting, schema inference
- **Phase 3:** Dashboard coordination patterns (shared filters, linked interactions) may need deeper ECharts research

Phases with standard patterns (skip research-phase):
- **Phase 1:** Well-documented patterns (Repository pattern, pytest fixtures, structlog usage)
- **Phase 2:** Established patterns (streaming imports, async HTTP, connection pooling)
- **Phase 5:** Template already exists in codebase

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions verified from PyPI; established ecosystem packages |
| Features | MEDIUM | Based on project context and domain knowledge; limited external validation |
| Architecture | HIGH | Well-documented patterns with code examples; standard Python practices |
| Pitfalls | MEDIUM | Project-specific issues from codebase audit; general patterns from training knowledge |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **External API authentication patterns:** Phase 4 (URL/API data source) needs research on OAuth, API key handling, and credential storage during planning
- **Dashboard coordination:** Phase 3 may need research on ECharts linked interactions and shared filter implementation
- **Localization strategy:** Current error messages are hardcoded in Chinese; need to define localization approach during implementation

## Sources

### Primary (HIGH confidence)
- PyPI package index - Version verification for all recommended packages
- Project codebase analysis - Current implementation patterns and concerns
- pandas.read_csv documentation - Streaming/chunking patterns
- pytest fixtures documentation - Test isolation patterns
- Python sqlite3 documentation - Parameterization limitations

### Secondary (MEDIUM confidence)
- SQLAlchemy connection pooling documentation - Connection pool patterns
- aiohttp client documentation - Async HTTP patterns
- Python asyncio documentation - Concurrent execution patterns
- "Working Effectively with Legacy Code" - Characterization testing approach

### Tertiary (LOW confidence)
- ECharts documentation - Dashboard grid layouts, map loading
- Web search results - ECharts dashboard patterns

---
*Research completed: 2026-04-04*
*Ready for roadmap: yes*
