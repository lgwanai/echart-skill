---
name: echart-skill
description: 使用本地 SQL/DuckDB 分析 Excel、CSV 或数据库数据，并生成可审计、可离线运行的 ECharts 图表、Dashboard 和分析报告。适用于数据导入、清洗、查询、同比环比、诊断分析、可视化和企业 BI 交付。
---

# EChart Data Analysis Skill

Use this skill to turn structured data into evidence-backed analysis and
standalone ECharts deliverables. The invariant is not “an HTML file exists”; it
is that the data, metric definition, analysis claim, visual expression, and live
browser result all reconcile.

## Required pipeline

Follow these stages for every analysis. Read only the references needed for the
requested deliverable.

1. **Resolve data and business scope**
   - Inspect schema with maintained CLIs; do not load large tables into context.
   - Run `python scripts/metrics_manager.py effective` before defining metrics,
     filters, governed entity sets, comparison scope, or business terminology.
   - Never invent fields or approximate a governed set with keyword matching.
2. **Assess data fitness**
   - Check date coverage, incomplete periods, nulls, duplicates, grain,
     uniqueness, units, currency, timezone, status filters, and known exclusions.
   - Use `scripts/data_quality.py` or `scripts/data_contract.py` when relevant.
3. **Query through the audited execution path**
   - Generate reviewable SQL and execute it with `scripts/sql_runner.py`,
     `scripts/db_cli.py`, or `scripts/db_manager.py`.
   - Never write temporary database connection code, heredoc Python,
     `duckdb.connect`, `psycopg.connect`, `pymysql.connect`, `create_engine`,
     `.cursor()`, or `cur.execute()`.
   - Write query results with `--out` so query hash and lineage metadata exist.
4. **Plan the analytical expression**
   - Read [analysis expression quality](workflow_specs/analysis_expression_quality.md).
   - Write an analysis-plan JSON and run
     `python scripts/validate_analysis_plan.py <plan.json>`.
   - Use Message → Relation → View. Select views through
     `references/chart_capabilities.json` or
     `python scripts/chart_capabilities.py <view-request.json>`.
   - Distinguish the hidden audit/source table from a visible analytical
     companion table.
5. **Bind evidence instead of restating it**
   - Read `workflow_specs/artifact_evidence_contract.md`.
   - Create a draft artifact manifest that references actual query result files.
   - Run `python scripts/artifact_manifest.py bind <output.html> <draft.json>`.
   - The binder computes query-result SHA-256, row count, date coverage, and
     binds query hashes, metric/scope fingerprints, comparisons, charts, and
     findings into the HTML.
6. **Render from maintained recipes and templates**
   - Read `references/examples/INDEX.md`, then the selected recipe completely.
   - Dashboard: read `workflow_specs/dashboard_workflow.md` and
     `workflow_specs/dashboard_runtime_quality.md`.
   - Report: read `workflow_specs/report_workflow.md`.
   - Use `workflow_specs/html_templates/dashboard_light.html` or
     `workflow_specs/html_templates/report_light.html` as the relevant shell.
7. **Run the complete delivery gate**
   - Run `python scripts/validate_delivery.py <output.html>`.
   - This combines static ECharts/runtime checks, governance checks, manifest
     reconciliation, and a real Playwright/Chromium render.
   - Any console error, page error, external request, missing ECharts instance,
     zero-size canvas/SVG, evidence mismatch, or invalid comparison blocks
     delivery.
   - `--allow-static-only` is a degraded exception only when browser execution
     is genuinely unavailable; disclose that reduced assurance.

## SQL execution contract

Preferred examples:

```bash
python scripts/schema_manager.py show <table>
python scripts/sql_runner.py --db workspace.duckdb --file queries/<task>.sql \
  --output json --out outputs/query_results/<task>.json
python scripts/sql_runner.py --profile <profile> --file queries/<task>.sql \
  --output json --out outputs/query_results/<task>.json
```

For one-off external connections, pass credentials only through approved
environment-backed CLI parameters such as `--password-env` or `--dsn-env`.
Project queries, connection profiles, outputs, logs, and generated packages are
local state and must never be added to the reusable skill release.

## Comparison and metric correctness

All YoY, QoQ, MoM, WoW, period, and cohort comparisons must declare:

- current and baseline start/end;
- complete or partial status;
- latest complete period;
- calendar type: calendar, fiscal, retail 4-4-5, or custom;
- alignment rule and comparability;
- visible current/baseline labels;
- evidence query IDs and metric IDs;
- identical current/baseline fingerprints for metric definition, entity scope,
  filters, unit, currency, and timezone.

YTD-versus-full-year and partial-versus-complete comparisons are blocking
failures. Fiscal and retail calendars align governed named periods rather than
being forced onto calendar-month boundaries.

An HTML comparison must contain both `analysis-comparison-contract` and
`analysis-artifact-manifest`. The declared windows must match each other and the
actual dates in the bound query result files.

## Findings and analytical depth

Every major finding must state What, baseline, Why status, Why, So what, next
check, evidence references, and limitations.

- `tested`: allowed only when the artifact manifest references an executed next
  check query.
- `hypothesis`: a plausible explanation that still needs testing.
- `unknown`: insufficient evidence; state the missing data.

Correlation, ranking, trend, anomaly, and composition detectors produce
descriptive candidates, not causal conclusions. Drill down through contribution,
segment, volume × rate/price, anomaly/data-quality, and stability/sample-size
checks when the data supports them.

## Visual and table contract

- Prefer position and length encodings over angle, area, volume, and decorative
  effects.
- A pie chart is limited to 2–3 positive categories and approximate share.
- Use a visible companion table for exact lookup, high-density comparison,
  exceptions, risk/action lists, or four-plus measures.
- Every chart still needs a default-hidden `查看数据` source table, chart-level
  statistical scope, data source, and evidence/query reference.
- Include units, readable labels, semantic colors, responsive sizing, and a
  text/table fallback. Do not rely on color alone.
- Do not invent a product, brand, industry label, or title that is absent from
  the request, governed scope, schema, and evidence.
- Mixed bar/line charts with different units or magnitudes require separate
  y-axes and explicit `yAxisIndex: 0` / `yAxisIndex: 1` assignment.

## Standalone HTML and runtime contract

- Inline ECharts and required local assets; no CDN, runtime loader, `fetch()` to
  external URLs, iframe/object/embed, self-navigation, or `file://` nesting.
- Load libraries before chart bootstrap. Use literal `</script>` closing tags.
- Serialize data with `json.dumps(..., ensure_ascii=False, default=str)`; never
  hand-write large JavaScript data objects or call `JSON.parse({...})`.
- Use real responsive chart dimensions and resize handling.
- Dashboard runtime rules cover map registration including accidental
  `chinaGeoJSON` references, PDF export compatibility including `color-mix()`,
  card/grid density, data-table controls, and export/download behavior.

## Routing references

| Request | Read |
|---|---|
| Import or cleaning | `workflow_specs/data_cleaning_workflow.md` |
| Chart selection | `workflow_specs/analysis_expression_quality.md`, `references/chart_capabilities.json` |
| Dashboard | `workflow_specs/dashboard_workflow.md`, `workflow_specs/dashboard_runtime_quality.md` |
| Report | `workflow_specs/report_workflow.md` |
| Domain analysis | `workflow_specs/expert_library/INDEX.md` |
| Domain dashboard | `workflow_specs/dashboard_expert_library/INDEX.md` |
| Individual commands or CLI detail | `commands/echart/*.md` |

When adding a reusable dashboard expert, start from
`workflow_specs/dashboard_expert_library/DASHBOARD_EXPERT_TEMPLATE.md`; never
place a project-specific dashboard or query in the skill.

## Release hygiene

Run:

```bash
bash package.sh
python scripts/validate_release_package.py dist/<package>.zip
```

The package uses an allowlist. Project SQL, database connection files, outputs,
logs, caches, tests, and local indexes are forbidden release content.
