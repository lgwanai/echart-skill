# Dashboard Workflow

Use this workflow when handling `/dashboard`, `/db`, `/仪表盘`, or any request for an interactive business dashboard.

## Principle

The Agent designs the dashboard. Python should not generate the final dashboard from a fixed renderer.
Use Python only to query data, calculate metrics, and validate standalone HTML.

## Required Steps

1. **Define the dashboard job**
   - Identify target user: executive, analyst, operator, growth, finance, sales, etc.
   - Identify operating cadence: real-time, daily, weekly, monthly, campaign review.
   - Identify the primary decision the dashboard should support.

2. **Infer industry and KPI tree**
   - Select KPI groups using the report workflow industry playbooks.
   - Build a KPI tree before choosing charts.
   - Avoid chart collections without a business hierarchy.

3. **Plan layout**
   - First row: KPI summary and key status.
   - Second row: trend and comparison.
   - Third row: structure/segment breakdown.
   - Diagnostic area: anomalies, funnel, retention, attribution, or drill-down tables where relevant.
   - Put filters where users expect them: time, channel, region, product, user segment.

4. **Query evidence**
   - Use DuckDB/SQL/Python to produce the exact data arrays needed by charts.
   - Keep query logic auditable; include key SQL in comments or appendix when appropriate.

5. **Author standalone HTML**
   - Inline ECharts and required local JS/CSS assets.
   - Do not depend on a Python dashboard renderer.
   - The Agent writes the HTML, layout, chart options, and narrative cards.
   - Validate with `scripts/validate_chart.py`.

## Dashboard Content Patterns

### Traffic / Growth

Required modules:

- KPI cards: UV/PV/session/conversion/retention where available
- Trend: traffic and conversion over time
- Funnel: stage conversion and drop-off
- Retention: cohort or repeat-visit view when data supports it
- Attribution: channel/campaign/page contribution

### Sales / E-commerce

Required modules:

- KPI cards: GMV/revenue/order count/AOV/quantity
- Trend: sales over time with comparison
- Structure: product/category/channel/region
- Attribution: drivers of latest change
- Risk: concentration, refund/discount/margin if available

### Finance

Required modules:

- KPI cards: revenue/cost/profit/margin/budget variance
- Trend: revenue vs cost/profit
- Structure: cost or expense breakdown
- Attribution: department/project/product contribution

## Visual Rules

- Use `workflow_specs/visual_templates/light.md` by default.
- Use the dark spec only when requested or when the context is command-center/monitoring.
- Keep UI dense, formal, and readable. This is an operating surface, not a marketing page.
- Do not put cards inside cards.
- Use stable grid dimensions so charts and labels do not shift layout.
- Include insight cards only when they contain specific numbers or clear business interpretation.

## Validation Rules

Before returning:

- Generated HTML must be standalone.
- ECharts and map assets must be inlined when used.
- Dashboard controller code must be inlined if interactive controls are used.
- Run `python scripts/validate_chart.py <output.html>` when an HTML dashboard is produced.
