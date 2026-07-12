# Project Management & Delivery Dashboard Expert

Use this dashboard expert for project-portfolio operating surfaces: status, milestones, schedule/cost variance, effort/utilization, task completion, and delivery risk.

## Dashboard Mission

Create a delivery operating surface that shows portfolio health, where schedule and cost variance concentrate, how resources are utilized, and which risks threaten on-time, on-budget delivery. The target user is a PMO lead or project manager who must decide where to escalate, rebalance resources, or replan.

## Required Modules

1. **KPI summary**
   - Purpose: show on-time rate, schedule variance, cost/effort variance, and at-risk project count at a glance.
   - Data needed: project/task fields with planned baselines for deltas.
   - Card: KPI cards with value, delta vs baseline, and scope note.

2. **Status distribution and trend**
   - Purpose: show portfolio health and how it shifts over time.
   - Data needed: status field + date.
   - Chart recipe: `references/examples/bar-simple.md` (stacked by status) and `references/examples/line-simple.md` for trend.

3. **Schedule variance by project/milestone (cross-analysis)**
   - Purpose: locate where slippage concentrates.
   - Data needed: planned vs actual dates + project/milestone.
   - Chart recipe: `references/examples/bar-simple.md` (slippage days) or Gantt from `references/examples/INDEX.md` (`custom-gantt`).

4. **Cost / effort planned vs actual**
   - Purpose: separate under-estimation from execution overrun.
   - Data needed: planned and actual cost/effort per project.
   - Chart recipe: grouped bar or waterfall from `references/examples/INDEX.md`.

5. **Resource utilization**
   - Purpose: expose over- and under-allocation and bottlenecks.
   - Data needed: effort by person/team/role.
   - Chart recipe: heatmap or `references/examples/bar-simple.md`.

6. **Delivery risk / overdue-blocked tasks**
   - Purpose: flag risks that threaten milestones.
   - Data needed: risk/issue records, overdue/blocked task counts, severity.
   - Module: risk table + severity bar; skip with a visible data-gap card if fields are absent.

7. **Data quality and scope note**
   - Purpose: state what the dashboard can and cannot prove.
   - Required visible note: project vs task grain, status mapping, whether planned dates/cost/effort and EV fields exist.

## Interaction Model

- Filters: period, project, team/owner, status, milestone type.
- Drill-down dimensions: project -> milestone phase -> owning team; risk -> dependency chain.
- Comparison controls: current vs previous snapshot; actual vs plan when fields exist.
- Tooltip content: status, slippage days, planned vs actual, utilization %, comparison value.
- Export/download behavior: dashboard PDF export and individual chart download.
- Theme behavior: page-level theme switch that updates all surfaces and charts.

## Geographic Rules

- Location field detection: use metadata, field names, and sample values (e.g., projects by site/region).
- Metric selection: prefer at-risk/delayed count, then schedule variance.
- When triggered, read `workflow_specs/dashboard_modules/city_sales_map.md`.
- Fallback when coordinates or map coverage are insufficient: visible data-gap card + region/team ranking bar.

## Diagnostic Modules

- Cross-analysis matrix: project x milestone type, team/owner x on-time rate, planned vs actual effort x project, resource x utilization x delay.
- Anomaly scan: healthy completion but worsening schedule variance, slippage concentration, effort overrun with stable scope, allocation imbalance, rising overdue/blocked tasks.
- Attribution path: schedule variance -> scope/effort/dependency/resource effect -> project -> milestone phase -> team.
- Data-gap cards: missing planned dates, missing planned cost/effort, missing EV fields.

## Layout Guidance

- Header and title rules: title must come from prompt/table/fields; stay domain-neutral when industry is unproven.
- KPI row: 4-5 cards (on-time rate, schedule variance, cost/effort variance, at-risk count).
- Primary charts row: status distribution/trend + schedule variance.
- Segment row: cost/effort planned vs actual + resource utilization.
- Diagnostic row: delivery risk/overdue-blocked + anomaly/attribution + data quality note.
- Responsive behavior: preserve chart heights and avoid cards inside cards.

## Chart Recipe Requirements

- Trend: `references/examples/line-simple.md`
- Ranking/contribution: `references/examples/bar-simple.md`
- Timeline: Gantt recipe (`custom-gantt`) from `references/examples/INDEX.md`.
- Cross-analysis: heatmap or grouped bar from `references/examples/INDEX.md`.
- Map: `workflow_specs/dashboard_modules/city_sales_map.md` then `references/examples/geo-map-scatter.md`
- Fallback: `references/examples/bar-simple.md`

## Validation Checklist

- Title is traceable to prompt/table/fields.
- At least 6 analytical modules are present when data supports them.
- Triggered location map module is present or has explicit fallback.
- Every chart cites its recipe context.
- Dashboard includes business interpretation cards, not only charts.
- No unsupported KPI or industry concept is invented; do not report schedule/cost variance or SPI/CPI without the required planned/EV fields.
