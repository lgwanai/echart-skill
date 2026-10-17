# Dashboard Workflow

Use this workflow when handling `/dashboard`, `/db`, `/仪表盘`, or any request for an interactive business dashboard.

## Principle

The Agent designs the dashboard: expert selection, analytical plan, interpretation,
and information architecture. The project compiler applies that explicit plan;
it does not invent business modules or conclusions from hardcoded industry rules.

## Project scheme discovery and reuse

Before planning, run `python scripts/project_dashboard.py resolve` from the user
project, using the absolute installed Skill script path. Discovery uses the nearest
project root; `--project-root` or `ECHART_PROJECT_ROOT` explicitly selects a root.
Never reuse an unrelated project's scheme. `project_data_context.py resolve`
also includes `project_dashboard` as a discovery summary.

Precedence: explicit task overrides > selected/default project scheme > built-in
defaults. A single registered scheme is selected automatically; multiple schemes
require a default or `--profile`. Missing registry uses built-in defaults without
writing files; orphan JSON, malformed configuration, unknown keys, missing expert
files or incompatible chart preferences block generation. Report and Dashboard
registries are separate, even when a project deliberately shares an expert note.

When asked to remember a Dashboard expert, layout or chart preference, preserve
unrelated settings and save/register the scheme in the **user project**, not the
Skill. Set the project default when requested. A temporary instruction must not
overwrite saved defaults. Resolve and validate after saving; future requests such
as “按项目默认方案生成看板” must reuse these files without another long prompt.

`config/dashboards/manifest.json`:

```json
{"version":1,"default":"operations","profiles":{"operations":"config/dashboards/operations.json"}}
```

Example `operations.json` (partial profiles inherit defaults):

```json
{
  "version": 1,
  "audience": "经营运营团队",
  "analysis": {
    "experts": [{"id":"project_operations","path":"config/dashboards/experts/operations.md","role":"primary","method_ids":["drivers"]}],
    "methods": [{"id":"drivers","instructions":"按项目指标口径拆解贡献，交叉验证主要驱动；缺字段时说明数据缺口。"}],
    "questions": ["哪些维度贡献了主要变化？"],
    "expert_notes": []
  },
  "layout": {
    "columns": 2,
    "accent": "#146358",
    "wide_charts": [],
    "sections": [{"id":"overview","title":"经营概览"},{"id":"diagnostics","title":"诊断与行动"}]
  },
  "charts": {"preferences":{"ranking":"bar","time":"line"},"avoid":["pie"]}
}
```

### Project experts

Start from `workflow_specs/dashboard_expert_library/DASHBOARD_EXPERT_TEMPLATE.md`,
but save business-specific Markdown in the project. Define its mission, required
modules, metrics/data prerequisites, cross-analysis, anomalies, attribution,
interaction needs and validation checks. Fill every applicable section; do not
insert executable plugins, credentials or canned conclusions.

Register each expert with `id`, project-relative `path`, `role` (`primary` or
`supporting`), and nonempty `method_ids` referencing `analysis.methods`. When
project experts exist there must be exactly one primary expert. Read every file
fully before planning; required expert analyses must be represented in methods,
not left only in prose. `expert_notes` supplies additional project guidance.
When no project expert is registered, select from the built-in Dashboard library;
do not substitute a report expert as the primary Dashboard planner.

Each configured method must appear in the output as `executed` with actual
audited query IDs, or `data_gap` with a visible reason. The Agent must check that
the query actually implements the method. Coverage checks are not proof of causal
claims. Expert/template content hashes enter the scheme fingerprint; changes
require re-reading and re-planning, not merely replacing a stale hash.

### Layout, preferences and build contract

- `layout.sections` controls exact module group order and headings. Each chart's
  `section` matches a configured ID. Chart order within a section follows the
  task specification. `columns` supports 1/2/3 desktop columns; mobile is one.
  `accent` is six-digit hex. `wide_charts` names stable chart IDs; the compiler
  may additionally promote leading, dense and unpaired cards to full width to
  prevent blank half-rows. This does not rewrite the saved scheme.
- Optional `layout.shell` is a project-contained passive HTML/CSS file with one
  complete head/body and exactly one `<!-- DASHBOARD_CONTENT -->`. No scripts,
  URL assets, event handlers or chart initialization. CSS may customize the
  appearance but cannot hide evidence or contradict the resolved grid/spans.
- `charts.preferences` maps relation to a supported compiler view, using the
  same capability catalog as reports. Deviations require a visible
  `view_override_reason` and a compatible validated analysis plan.
- Author a spec with `artifact_type: "dashboard"`, `analysis_plan`, `charts`,
  and `dashboard`. The `dashboard` object uses the report workflow's
  `title`, `scope`, `limitations`, `profile_sha256`, `sections`, `methods` fields,
  plus a nonempty `kpis` list. Bind all findings/comparisons in the evidence
  manifest. Query results require their audited `.meta.json` sidecars.
- Each KPI is a reference, **not a hand-entered value or a calculation**:
  `{"id":"net_sales","label":"净销售额","unit":"元","scope":"当前已完成周期净额","query_id":"q_total","row":0,"field":"net_sales"}`.
  The query must already compute the correct aggregate. Row is zero-based;
  absent/non-numeric/non-finite values fail, never silently become zero.
- Companion/primary tables use `table_columns` and `table_reason` from the
  validated plan and actual query rows. Source tables remain default-hidden.

```bash
python /path/to/echart-skill/scripts/project_dashboard.py --project-root /path/to/project resolve
python /path/to/echart-skill/scripts/project_dashboard.py --project-root /path/to/project build outputs/dashboard-spec.json --evidence outputs/evidence.json --output outputs/dashboard.html
# Optional global arguments before resolve/build:
# --profile operations --overrides outputs/task-dashboard-overrides.json
```

Use the same profile and overrides for resolve/build. Override objects merge,
lists replace; they are not saved. `chart_builder.py` delegates Dashboard specs
to this gated entry point; legacy `--shell` Dashboard builds cannot bypass an
existing registry. Builds bind an immutable `project-dashboard-contract`, verify
KPI/series evidence, methods, layout and real desktop/mobile rendering, then
atomically replace the output. Failure preserves the last delivered artifact.

This path supports the nine common compiler views, tooltip/source-table access,
SVG downloads and PDF export (with print fallback). It is an offline snapshot,
not live data: no fake refresh, polling, theme/filter/drill-down controls without
an implemented data/runtime contract. Specialized maps, custom interactive
filters or other unsupported expert requirements need a separately verified
implementation or an explicitly explained fallback; do not silently drop them
or claim they were applied. Project schemes never disable quality/evidence gates.

## Required Steps

1. **Define the dashboard job**
   - Read `workflow_specs/analysis_expression_quality.md` completely.
   - Identify target user: executive, analyst, operator, growth, finance, sales, etc.
   - Identify operating cadence: real-time, daily, weekly, monthly, campaign review.
   - Identify the primary decision the dashboard should support.
   - Query the maximum available business date, determine the latest complete period, and record it before calculating any YoY/MoM metric.
   - Define the dashboard title from the user request, table/file name, and actual fields. Do not invent a product, brand, or industry label that is not present in the data or prompt.
   - Title rule: if the user uploads a sales table and does not name a specific industry, use a neutral title such as `销售数据经营 Dashboard`, `销售表现分析 Dashboard`, or `<表名> Dashboard`. Never infer a narrow category such as white liquor, cosmetics, SaaS, or apparel unless the data contains that category or the user says it.

2. **Infer industry and KPI tree**
   - Read `workflow_specs/dashboard_expert_library/INDEX.md`.
   - Use registered project experts when configured; otherwise select one primary dashboard expert and optional supporting experts from the dashboard expert library.
   - Read the selected expert Markdown files completely.
   - Build KPI groups from selected expert files, not from hardcoded Python rules.
   - Convert selected experts' `Cross Analysis Matrix`, `Anomaly Patterns`, and `Deep Attribution Paths` into dashboard diagnostic modules.
   - Build a KPI tree before choosing charts.
   - Avoid chart collections without a business hierarchy.

3. **Plan layout**
   - Save the message/relation/view/table/finding decisions as an analysis-plan JSON and run `python scripts/validate_analysis_plan.py <plan.json>` before selecting recipes or writing HTML.
   - First row: KPI summary and key status.
   - Second row: trend and comparison.
   - Third row: structure/segment breakdown.
   - Diagnostic area: anomalies, funnel, retention, attribution, or drill-down tables where relevant.
   - Treat the hidden `查看数据` table as an audit source toggle. Add a visible compact companion table when exact lookup, exception handling, more than 15 categories, or four-plus measures make it decision-relevant.
   - Include at least one cross-analysis module and one anomaly/attribution module when data supports them.
   - Put filters where users expect them: time, channel, region, product, user segment.
   - If metadata, schema, or sample values contain a city field and a sales/volume/transaction metric, read `workflow_specs/dashboard_modules/city_sales_map.md` completely and include its map module unless the user explicitly excludes geography.
   - Minimum depth for business dashboards: include at least 6 analytical modules when data supports them: KPI cards, trend, ranking/contribution, structure/composition, geographic city module when triggered, cross-analysis, anomaly/attribution, and data quality/scope note.
   - A dashboard with only 2-3 charts is incomplete unless the dataset truly has too few fields; in that case, show a data limitation note and explain which missing fields prevent deeper analysis.

4. **Query evidence**
   - Use DuckDB/SQL/Python to produce the exact data arrays needed by charts.
   - Reuse one explicit comparison boundary across headline KPIs, charts, rankings, tables, price analysis, attribution, and narrative. If the latest complete month is July, every YoY query must compare January–July on both sides.
   - Keep query logic auditable; include key SQL in comments or appendix when appropriate.
   - Read `references/chart_guide.md`. Compile supported common views from query-result files using `scripts/chart_builder.py`; do not rewrite options/runtime. For specialized views only, retrieve the selected archived recipe through `scripts/reference_assets.py get <name>` and verify the adapted option and local dependencies.

5. **Author standalone HTML**
   - Use the project compiler's responsive shell or the resolved project shell. For separately verified custom dashboards, read `workflow_specs/html_templates/dashboard_light.html` completely as the shell reference; do not override an existing project scheme silently.
   - Use `workflow_specs/visual_templates/light.md` or `dark.md` only as visual direction; do not use Markdown visual notes as the final HTML shell.
   - Read `workflow_specs/dashboard_runtime_quality.md` completely and apply its runtime quality gate.
   - Inline ECharts and required local JS/CSS assets.
   - The Agent owns layout and narrative; the compiler owns chart components. The project generator assembles section-aware slots. Custom builds without a registered scheme may use one `<!-- ECHART_CHARTS -->` or exact named slots; never include duplicate chart bootstrap.
   - Bind evidence and validate with `scripts/validate_delivery.py`; static checks alone are not delivery verification.

## Dashboard Content Patterns

Dashboard modules are defined by the selected dashboard expert files in
`workflow_specs/dashboard_expert_library/`.

For each selected expert:

- Use its `Dashboard Modules` section as candidate modules.
- Use its `Core Metrics` section for KPI cards.
- Use its `Required Data Checks` section to create explicit data-gap notes.
- Use its `Cross Analysis Matrix` section for heatmaps, segmented bars, scatter plots, or comparison matrices.
- Use its `Anomaly Patterns` section for alert cards and abnormal segment markers.
- Use its `Deep Attribution Paths` section for driver trees, waterfall charts, and drill-down tables.
- Use its `Report Questions` section to decide which insight cards are worth showing.
- Use its `Interaction Model`, `Layout Guidance`, `Chart Recipe Requirements`, and `Validation Checklist` to drive dashboard behavior and final checks.

## Geographic City Module

When city-level geography is detected in metadata, schema, or sample values:

1. Read `workflow_specs/dashboard_modules/city_sales_map.md`.
2. Select the real city field and the real sales/volume/transaction metric from the user data.
3. Read the chart recipe Markdown required by that module, normally `references/examples/geo-map-scatter.md`.
4. Generate the city map chart one chart at a time, then assemble it into the dashboard shell.
5. If coordinates or map coverage are insufficient, show a data-gap note and use the ranked bar fallback from `references/examples/bar-simple.md`.
6. If the final dashboard does not contain either a rendered city map (`geo` + `effectScatter`) or the explicit ranked-bar fallback plus data-gap note, the dashboard fails validation and must be regenerated.

This module is optional only when:

- The user explicitly says not to include geography.
- The city field is present but no meaningful metric exists and count fallback would be misleading.
- All city values are unusable after inspection; in that case the dashboard must show a data quality note.

If no dashboard expert strongly matches, select `general_business_dashboard.md` and build:

- KPI cards
- trend chart
- dimension breakdown
- top drivers table
- risk/anomaly cards
- data quality note

## Visual Rules

- Apply the project scheme and generator shell. Use `workflow_specs/html_templates/dashboard_light.html` as reference for separately verified custom dashboards.
- Read `workflow_specs/visual_templates/light.md` by default as supplemental visual direction.
- Read and apply the dark spec only when requested or when the context is command-center/monitoring, then adapt the dashboard shell tokens without weakening its structure.
- Keep UI dense, formal, and readable. This is an operating surface, not a marketing page.
- Do not put cards inside cards.
- Use stable grid dimensions so charts and labels do not shift layout.
- Include insight cards only when they contain specific numbers or clear business interpretation.
- The generated CSS must visibly implement the dashboard shell: background, surface, typography, borders, chart panel spacing, KPI card hierarchy, semantic colors, toolbar, diagnostic panel, print rules, and responsive behavior.
- Theme switching must be page-level, not chart-only: the HTML root or dashboard root must toggle `data-theme`, and CSS tokens must update page background, header, toolbar, cards, charts, diagnostics, buttons, and toasts.
- Before returning, inspect the HTML/CSS and confirm it does not look like unstyled default HTML.

## Validation Rules

Before returning:

- Read `workflow_specs/artifact_evidence_contract.md`, bind every query result to
  the final HTML with `scripts/artifact_manifest.py`, and run the combined
  `scripts/validate_delivery.py` gate.
- The analysis-plan JSON must pass `scripts/validate_analysis_plan.py`; every view title states a finding rather than only a topic.
- Any YoY/MoM/period comparison must declare both windows, completeness status, and latest complete period. Partial-versus-complete or YTD-versus-full-year is a blocking failure; a caveat does not downgrade it to a warning.
- If the visible HTML contains 同比/环比/同期/YoY/QoQ/MoM/WoW, embed the version-1
  `analysis-comparison-contract` JSON described in
  `analysis_expression_quality.md`. The visible current/baseline labels and the
  embedded dates must agree; missing or misaligned contracts fail
  `scripts/validate_chart.py`.
- Every major finding must complete What, baseline, Why status, Why, So what, next check, evidence references, and limitations. Execute at least one next check when the needed fields exist, or show the data gap.
- Read and apply `workflow_specs/dashboard_runtime_quality.md`.
- Generated HTML must be standalone.
- ECharts and map assets must be inlined when used.
- Dashboard controller code must be inlined if interactive controls are used.
- No runtime external loaders are allowed: no `script.src = https`, no `fetch(https)`, no injected CDN script tags.
- No invalid global declarations are allowed: use `window.dashboardCharts = []`, never `var window.dashboardCharts = []`.
- No `color-mix()`, `oklch()`, `oklab()`, `lab()`, or `lch()` in dashboard CSS when PDF export uses html2canvas.
- Map bootstrap must rely on inlined map JS registration; do not reference `chinaGeoJSON` unless it is explicitly defined in the same HTML.
- The chosen HTML shell and visual direction file must have been read and translated into CSS tokens/classes.
- The title must be traceable to the user prompt, table/file name, or actual data fields. If it contains a specific industry/product term, that term must exist in the prompt or evidence.
- The dashboard must include the minimum analytical depth modules unless the data lacks required fields, and any skipped module must have a visible data-gap reason.
- If city geography and sales/volume metrics are present, the final HTML must include the city map module or the documented fallback. Missing the module is a blocking failure.
- The dashboard must include at least one business interpretation card when data supports it; it cannot be only charts.
- The dashboard should not stop at KPI totals; it must include cross-analysis, anomaly, or attribution diagnostics when the required fields exist.
- Run `python scripts/validate_delivery.py <output.html>` when an HTML dashboard is produced.
- The combined gate requires live Chromium rendering when available and also runs the browser-free static checks for forbidden URL assets, iframe/object/embed usage, runtime self-load/navigation patterns, custom JS syntax errors, PDF-incompatible CSS, missing controller/export/download pieces, and map registration issues. `--allow-static-only` is an explicitly degraded exception.
- When browser automation is available, use it only as an extra smoke test through `file://`: no page errors, no console errors, expected chart canvas count, map canvas when triggered, empty external script list, working PDF export, and working chart download.
