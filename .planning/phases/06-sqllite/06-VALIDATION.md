---
phase: 6
slug: sqllite
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | pyproject.toml (existing) |
| **Quick run command** | `pytest tests/test_data_merger.py -x -v` |
| **Full suite command** | `pytest tests/ --cov=scripts --cov-report=term-missing` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_data_merger.py -x -v`
- **After every plan wave:** Run `pytest tests/ --cov=scripts --cov-report=term-missing`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | MERGE-01 | unit | `pytest tests/test_data_merger.py::TestMergeConfig -v` | ❌ W0 | ⬜ pending |
| 06-01-02 | 01 | 1 | MERGE-01 | unit | `pytest tests/test_data_merger.py::TestMergeTables -v` | ❌ W0 | ⬜ pending |
| 06-02-01 | 02 | 2 | MERGE-02 | unit | `pytest tests/test_data_merger.py::TestExport -v` | ❌ W0 | ⬜ pending |
| 06-02-02 | 02 | 2 | MERGE-03 | unit | `pytest tests/test_data_merger.py::TestImport -v` | ❌ W0 | ⬜ pending |
| 06-02-03 | 02 | 2 | MERGE-04 | integration | `pytest tests/test_data_merger.py::TestCLI -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_data_merger.py` — Merge, export, import tests
- [ ] No framework install needed — pytest already configured

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Large table merge performance | MERGE-01 | Requires large dataset | Merge 3 tables with 100K+ rows each, verify memory usage |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
