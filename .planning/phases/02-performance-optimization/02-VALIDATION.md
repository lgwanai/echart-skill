---
phase: 2
slug: performance-optimization
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | pyproject.toml (existing) |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ --cov=scripts --cov-report=term-missing` |
| **Estimated runtime** | ~45 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ --cov=scripts --cov-report=term-missing`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 45 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | PERF-02 | unit | `pytest tests/test_database.py -v` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | PERF-05 | unit | `pytest tests/test_database.py::test_wal_mode -v` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | PERF-01 | unit | `pytest tests/test_streaming_import.py -v` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 2 | PERF-03 | unit | `pytest tests/test_async_geocoding.py -v` | ❌ W0 | ⬜ pending |
| 02-04-01 | 04 | 2 | PERF-04 | unit | `pytest tests/test_server_lifecycle.py -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_database.py` — connection pool tests
- [ ] `tests/test_streaming_import.py` — large file import tests
- [ ] `tests/test_async_geocoding.py` — async geocoding tests
- [ ] `tests/test_server_lifecycle.py` — server lifecycle tests

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Memory usage for 100MB file | PERF-01 | Requires memory profiling tools | Import 100MB Excel file, monitor memory with `top` or `psutil` |
| Actual geocoding latency reduction | PERF-03 | Requires network calls | Geocode 50 addresses, compare before/after timing |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 45s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
