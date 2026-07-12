# Finance & Management Dashboard Expert

Use this dashboard expert for finance and management-accounting operating surfaces: revenue, cost, expense, profit, margin, budget variance, cost center, cash, and receivables.

## Dashboard Mission

Create a decision-oriented finance operating surface that shows whether the business is on budget, where profit and margin are moving, which cost centers drive variance, and whether cash/receivable risk is building. The target user is a finance manager or business owner who must decide where to inspect spend and margin next — not merely read the P&L.

## Required Modules

1. **KPI summary**
   - Purpose: show revenue, cost, profit, margin, and budget variance at a glance.
   - Data needed: P&L numeric fields; baseline (previous period, budget, or target) for deltas.
   - Card: KPI cards with value, delta vs baseline, and scope note.

2. **Revenue-cost-profit trend**
   - Purpose: show direction and where lines diverge.
   - Data needed: date field + revenue/cost/profit.
   - Chart recipe: `references/examples/line-simple.md` (dual axis when margin % is shown alongside amounts).

3. **Expense / cost structure**
   - Purpose: show spend composition by cost center, department, or category.
   - Data needed: categorical dimension + expense/cost amount.
   - Chart recipe: `references/examples/bar-simple.md` or `references/examples/pie-simple.md` when categories are few.

4. **Budget vs actual variance**
   - Purpose: show favorable/unfavorable variance and its build-up.
   - Data needed: budget and actual per category/period.
   - Chart recipe: waterfall recipe from `references/examples/INDEX.md` (search `bar-waterfall`).

5. **Margin / expense-ratio analysis (cross-analysis)**
   - Purpose: expose profitable vs dilutive growth and scale efficiency.
   - Data needed: revenue + cost/margin by product/region/department.
   - Chart recipe: grouped/stacked bar or scatter from `references/examples/INDEX.md`.

6. **Cash / receivable risk**
   - Purpose: flag collection risk and aging concentration.
   - Data needed: receivable balance + aging bucket or due date.
   - Module: aging bar/table; skip with a visible data-gap card if fields are absent.

7. **Data quality and scope note**
   - Purpose: state what the dashboard can and cannot prove.
   - Required visible note: period grain, currency, whether figures are budget/actual/forecast, and missing fields.

## Interaction Model

- Filters: period, cost center/department, category, product/region.
- Drill-down dimensions: cost center -> category -> project; product/region -> margin.
- Comparison controls: actual vs previous period vs budget when fields exist.
- Tooltip content: amount, share, variance vs baseline, margin %.
- Export/download behavior: dashboard PDF export and individual chart download.
- Theme behavior: page-level theme switch that updates all surfaces and charts.

## Geographic Rules

- City field detection: use metadata, field names, and sample values (e.g., revenue/receivables by city).
- Metric selection: prefer revenue, then profit, then receivable balance.
- When triggered, read `workflow_specs/dashboard_modules/city_sales_map.md`.
- Fallback when coordinates or map coverage are insufficient: visible data-gap card + region ranking bar.

## Diagnostic Modules

- Cross-analysis matrix: time x P&L line, cost center x category, product/region x margin.
- Anomaly scan: margin declining while revenue grows, expense outpacing revenue, variance concentrated in one owner.
- Attribution path: profit change -> revenue/cost/expense effect -> cost center/category -> owner.
- Data-gap cards: missing budget, missing cost fields, missing receivable/aging.

## Layout Guidance

- Header and title rules: title must come from prompt/table/fields; stay domain-neutral when industry is unproven.
- KPI row: 4-5 cards (revenue, cost, profit, margin, budget variance).
- Primary charts row: revenue-cost-profit trend + budget-variance waterfall.
- Segment row: expense/cost structure + margin cross-analysis.
- Diagnostic row: cash/receivable risk + anomaly/attribution + data quality note.
- Responsive behavior: preserve chart heights and avoid cards inside cards.

## Chart Recipe Requirements

- Trend: `references/examples/line-simple.md`
- Ranking/contribution: `references/examples/bar-simple.md`
- Structure: `references/examples/pie-simple.md` or bar fallback.
- Variance: waterfall recipe (`bar-waterfall`) from `references/examples/INDEX.md`.
- Map: `workflow_specs/dashboard_modules/city_sales_map.md` then `references/examples/geo-map-scatter.md`
- Fallback: `references/examples/bar-simple.md`

## Validation Checklist

- Title is traceable to prompt/table/fields.
- At least 6 analytical modules are present when data supports them.
- Triggered city map module is present or has explicit fallback.
- Every chart cites its recipe context.
- Dashboard includes business interpretation cards, not only charts.
- No unsupported KPI or industry concept is invented; do not report budget attainment, margin, or receivable risk without the required fields.
