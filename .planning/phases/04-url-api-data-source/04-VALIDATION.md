---
phase: 4
slug: url-api-data-source
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | pyproject.toml (existing) |
| **Quick run command** | `pytest tests/test_url_data_source.py -x -v` |
| **Full suite command** | `pytest tests/ --cov=scripts --cov-report=term-missing` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_url_data_source.py -x -v`
- **After every plan wave:** Run `pytest tests/ --cov=scripts --cov-report=term-missing`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | DATA-02 | unit | `pytest tests/test_url_data_source.py::TestAuthConfig -v` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | DATA-01 | unit | `pytest tests/test_url_data_source.py::TestURLFetch -v` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 2 | DATA-01 | unit | `pytest tests/test_url_data_source.py::TestImportFromURL -v` | ❌ W0 | ⬜ pending |
| 04-02-02 | 02 | 2 | DATA-03 | unit | `pytest tests/test_url_data_source.py::TestSchemaInference -v` | ❌ W0 | ⬜ pending |
| 04-02-03 | 02 | 2 | DATA-04 | unit | `pytest tests/test_url_data_source.py::TestRefresh -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_url_data_source.py` — URL fetch, auth, schema inference, refresh tests
- [ ] No framework install needed — pytest, pytest-asyncio, respx already configured

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live API import | DATA-01 | Requires real network calls | Import data from a real public API endpoint |
| Bearer token with real API | DATA-02 | Requires real authentication | Test with a real API that requires Bearer token |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
