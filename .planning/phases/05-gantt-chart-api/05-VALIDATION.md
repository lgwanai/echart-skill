---
phase: 5
slug: gantt-chart-api
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | pyproject.toml (existing) |
| **Quick run command** | `pytest tests/test_gantt_chart.py -x -v` |
| **Full suite command** | `pytest tests/ --cov=scripts --cov-report=term-missing` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_gantt_chart.py -x -v`
- **After every plan wave:** Run `pytest tests/ --cov=scripts --cov-report=term-missing`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | CHART-01 | unit | `pytest tests/test_gantt_chart.py::TestGanttTask -v` | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | CHART-01 | unit | `pytest tests/test_gantt_chart.py::TestGenerateGanttOption -v` | ❌ W0 | ⬜ pending |
| 05-02-01 | 02 | 1 | CHART-01 | unit | `pytest tests/test_gantt_chart.py::TestGenerateGanttHTML -v` | ❌ W0 | ⬜ pending |
| 05-02-02 | 02 | 1 | CHART-02 | manual | Review SKILL.md Gantt section | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_gantt_chart.py` — Gantt task validation and option generation tests
- [ ] No framework install needed — pytest already configured

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Gantt renders correctly in browser | CHART-01 | Requires visual verification | Open generated HTML, verify bars render correctly |
| SKILL.md documentation is clear | CHART-02 | Requires documentation review | Review SKILL.md Gantt section for clarity |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
