---
phase: 1
slug: security-quality-foundation
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-04
updated: 2026-04-04
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | pyproject.toml (Wave 0 creates) |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ --cov=scripts --cov-report=term-missing` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ --cov=scripts --cov-report=term-missing`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | QUAL-03 | unit | `pytest tests/conftest.py -v --collect-only` | Wave 0 task | ⬜ pending |
| 01-01-02 | 01 | 1 | SEC-01, SEC-02 | unit | `pytest tests/test_validators.py -v` | Wave 0 task | ⬜ pending |
| 01-01-03 | 01 | 1 | SEC-01 | unit | `pytest tests/test_data_exporter.py -v` | Wave 0 task | ⬜ pending |
| 01-01-04 | 01 | 1 | SEC-01 | unit | `pytest tests/test_data_cleaner.py -v` | Wave 0 task | ⬜ pending |
| 01-02-01 | 02 | 1 | QUAL-01 | unit | `pytest tests/test_logging_config.py -v` | Wave 0 task | ⬜ pending |
| 01-02-02 | 02 | 1 | QUAL-01 | grep | `grep -n "print(" scripts/chart_generator.py` | N/A | ⬜ pending |
| 01-02-03 | 02 | 1 | QUAL-01 | grep | `grep -n "print(" scripts/server.py` | N/A | ⬜ pending |
| 01-02-04 | 02 | 1 | QUAL-01 | grep | `grep -n "print(" scripts/data_exporter.py` | N/A | ⬜ pending |
| 01-03-01 | 03 | 2 | SEC-03 | unit | `pytest tests/test_config.py -v` | Wave 0 task | ⬜ pending |
| 01-03-02 | 03 | 2 | SEC-04 | unit | `pytest tests/test_server_security.py -v` | Wave 0 task | ⬜ pending |
| 01-04-01 | 04 | 2 | QUAL-04 | unit | `pytest tests/test_data_importer.py -v` | Wave 0 task | ⬜ pending |
| 01-04-02 | 04 | 2 | QUAL-04 | unit | `pytest tests/test_chart_generator.py -v` | Wave 0 task | ⬜ pending |
| 01-05-01 | 05 | 3 | QUAL-05 | integration | `pytest tests/test_integration.py -v` | Wave 0 task | ⬜ pending |
| 01-05-02 | 05 | 3 | QUAL-06 | coverage | `pytest --cov=scripts --cov-fail-under=80` | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Wave 0 tasks are embedded within each plan's first task:
- Plan 01 Task 1 creates: `tests/conftest.py`, `tests/test_validators.py`
- Plan 01 Task 3 creates: `tests/test_data_exporter.py`
- Plan 01 Task 4 creates: `tests/test_data_cleaner.py`
- Plan 02 Task 1 creates: `tests/test_logging_config.py`
- Plan 03 Task 1 creates: `tests/test_config.py`
- Plan 03 Task 2 creates: `tests/test_server_security.py`
- Plan 04 Task 1 creates: `tests/test_data_importer.py`
- Plan 04 Task 2 creates: `tests/test_chart_generator.py`
- Plan 05 Task 1 creates: `tests/test_integration.py`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Log file output format | QUAL-01 | Verify structured JSON in logs/echart-skill.log | Run any script, check logs/echart-skill.log for JSON format |
| Deprecation warning | SEC-03 | Verify user sees migration message | Set BAIDU_AK in config.txt, run chart_generator, verify warning printed |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (embedded in first task of each plan)
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** ready for execution
