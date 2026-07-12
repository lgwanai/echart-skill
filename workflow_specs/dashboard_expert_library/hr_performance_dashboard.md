# HR & Performance Dashboard Expert

Use this dashboard expert for human-resources operating surfaces: headcount, attrition, performance appraisal, KPI/OKR scores, compensation, recruitment funnel, and training.

## Dashboard Mission

Create a workforce operating surface that shows headcount health, where attrition concentrates, whether performance scoring is fair and discriminating, how the recruiting pipeline performs, and whether pay aligns with performance. The target user is an HR business partner or manager who must decide where to intervene on retention, hiring, or performance calibration.

## Required Modules

1. **KPI summary**
   - Purpose: show headcount, hires, exits, turnover rate, and offer acceptance at a glance.
   - Data needed: headcount/event fields; baseline period for deltas.
   - Card: KPI cards with value, delta vs baseline, and scope note.

2. **Headcount trend and structure**
   - Purpose: show net workforce change and composition.
   - Data needed: date + headcount; dimension (department/level/tenure).
   - Chart recipe: `references/examples/line-simple.md` for trend, `references/examples/bar-simple.md` for structure.

3. **Attrition breakdown**
   - Purpose: locate where turnover concentrates.
   - Data needed: exits + department/tenure/manager; exit type if available.
   - Chart recipe: `references/examples/bar-simple.md` (stacked by voluntary/involuntary when field exists).

4. **Performance score distribution (cross-analysis)**
   - Purpose: expose grade inflation, clustering, or lenient/harsh raters.
   - Data needed: performance score/rating + department/manager.
   - Chart recipe: distribution/histogram or grouped bar from `references/examples/INDEX.md`.

5. **Recruitment funnel**
   - Purpose: show pipeline conversion and drop points.
   - Data needed: stage counts (applied -> screened -> interviewed -> offered -> accepted).
   - Chart recipe: `references/examples/INDEX.md` funnel recipe.

6. **Pay-for-performance / compensation**
   - Purpose: check alignment of pay with performance and level.
   - Data needed: compensation + performance/level.
   - Module: scatter or grouped bar; skip with a visible data-gap card if compensation is absent.

7. **Data quality and scope note**
   - Purpose: state what the dashboard can and cannot prove.
   - Required visible note: snapshot vs event grain, whether exit type/targets/pay exist, and privacy scope (aggregated groups).

## Interaction Model

- Filters: period, department, level, tenure band, location.
- Drill-down dimensions: department -> manager -> tenure/level; hire cohort -> retention.
- Comparison controls: current vs previous period when a date field exists.
- Tooltip content: count, rate, share, comparison value.
- Export/download behavior: dashboard PDF export and individual chart download.
- Theme behavior: page-level theme switch that updates all surfaces and charts.

## Geographic Rules

- City field detection: use metadata, field names, and sample values (e.g., headcount/attrition by site).
- Metric selection: prefer headcount, then attrition rate.
- When triggered, read `workflow_specs/dashboard_modules/city_sales_map.md`.
- Fallback when coordinates or map coverage are insufficient: visible data-gap card + location ranking bar.

## Diagnostic Modules

- Cross-analysis matrix: tenure x attrition, department/manager x performance distribution, level x compensation x performance.
- Anomaly scan: attrition concentration, rating clustering/inflation, top performers leaving, offer-acceptance drop.
- Attribution path: turnover change -> mix effect vs within-segment rate -> department/manager/tenure.
- Data-gap cards: missing exit type, missing targets, missing compensation.

## Layout Guidance

- Header and title rules: title must come from prompt/table/fields; stay domain-neutral when industry is unproven.
- KPI row: 4-5 cards (headcount, hires, exits, turnover rate, offer acceptance).
- Primary charts row: headcount trend + attrition breakdown.
- Segment row: performance distribution + recruitment funnel.
- Diagnostic row: pay-for-performance + anomaly/attribution + data quality note.
- Responsive behavior: preserve chart heights and avoid cards inside cards.

## Chart Recipe Requirements

- Trend: `references/examples/line-simple.md`
- Ranking/contribution: `references/examples/bar-simple.md`
- Distribution: histogram/box recipe from `references/examples/INDEX.md`.
- Funnel: funnel recipe from `references/examples/INDEX.md`.
- Map: `workflow_specs/dashboard_modules/city_sales_map.md` then `references/examples/geo-map-scatter.md`
- Fallback: `references/examples/bar-simple.md`

## Validation Checklist

- Title is traceable to prompt/table/fields.
- At least 6 analytical modules are present when data supports them.
- Triggered city map module is present or has explicit fallback.
- Every chart cites its recipe context.
- Dashboard includes business interpretation cards, not only charts.
- No unsupported KPI or industry concept is invented; do not report regretted attrition, KPI/OKR attainment, or pay equity without the required fields, and respect privacy by showing aggregated groups.
