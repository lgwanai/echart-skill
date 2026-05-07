---
phase: 3
slug: dashboard-layouts
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | pyproject.toml (existing) |
| **Quick run command** | `pytest tests/test_dashboard_generator.py tests/test_dashboard_schema.py -x -v` |
| **Full suite command** | `pytest tests/ --cov=scripts --cov-report=term-missing` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_dashboard_generator.py tests/test_dashboard_schema.py -x -v`
- **After every plan wave:** Run `pytest tests/ --cov=scripts --cov-report=term-missing`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | DASH-02 | unit | `pytest tests/test_dashboard_schema.py -v` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | DASH-02 | unit | `pytest tests/test_dashboard_schema.py::TestSchemaGeneration -v` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 1 | DASH-01 | unit | `pytest tests/test_dashboard_generator.py::TestGridLayout -v` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 1 | DASH-01 | unit | `pytest tests/test_dashboard_generator.py::TestChartPositioning -v` | ❌ W0 | ⬜ pending |
| 03-02-03 | 02 | 2 | DASH-03 | unit | `pytest tests/test_dashboard_generator.py::TestHTMLGeneration -v` | ❌ W0 | ⬜ pending |
| 03-02-04 | 02 | 2 | DASH-03 | integration | `pytest tests/test_dashboard_generator.py::TestHTMLRendering -v` | ❌ W0 | ⬜ pending |
| 03-02-05 | 02 | 2 | DASH-04 | integration | `pytest tests/test_dashboard_generator.py::TestCLI -v` | ❌ W0 | ⬜ pending |
| 03-02-06 | 02 | 2 | DASH-04 | integration | `pytest tests/test_dashboard_generator.py::TestEndToEnd -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_dashboard_generator.py` — unit and integration tests for dashboard generation
- [ ] `tests/test_dashboard_schema.py` — pydantic model validation tests

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dashboard renders in browser | DASH-03 | Requires visual verification in browser | Open generated HTML in browser, verify all charts render correctly |
| Responsive layout behavior | DASH-01 | Requires manual resize testing | Resize browser window, verify charts resize correctly |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
