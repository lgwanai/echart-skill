# Manufacturing & Quality Dashboard Expert

Use this dashboard expert for production and quality operating surfaces: output vs plan, yield/defect rate, OEE, downtime, scrap/rework, and defect attribution.

## Dashboard Mission

Create a production operating surface that shows whether output meets plan, where yield and quality break down, how OEE loss splits across availability/performance/quality, and which lines, shifts, machines, or defect types drive loss. The target user is a plant or quality manager who must decide where to intervene on a line, shift, or process step.

## Required Modules

1. **KPI summary**
   - Purpose: show output vs plan, first-pass yield, OEE, and defect rate at a glance.
   - Data needed: production/quality fields; baseline period or plan for deltas.
   - Card: KPI cards with value, delta vs baseline, and scope note.

2. **Output trend vs plan**
   - Purpose: show attainment and direction by line.
   - Data needed: date + actual output; planned output if available.
   - Chart recipe: `references/examples/line-simple.md` (actual vs plan series).

3. **Yield / defect rate breakdown (cross-analysis)**
   - Purpose: locate where quality loss concentrates.
   - Data needed: good vs total counts + line/shift/product/machine.
   - Chart recipe: `references/examples/bar-simple.md` (grouped by shift/line) or heatmap from `references/examples/INDEX.md`.

4. **OEE component breakdown**
   - Purpose: show whether loss is availability, performance, or quality driven.
   - Data needed: OEE inputs (availability, performance, quality).
   - Chart recipe: stacked/grouped bar from `references/examples/INDEX.md`; show only components that exist.

5. **Defect Pareto**
   - Purpose: find the dominant defect types and originating stations.
   - Data needed: defect count by type + station/line.
   - Chart recipe: Pareto bar from `references/examples/INDEX.md`.

6. **Downtime by cause**
   - Purpose: expose recurring vs one-off stoppages.
   - Data needed: downtime hours + cause + line/machine.
   - Module: downtime bar; skip with a visible data-gap card if timestamps/causes are absent.

7. **Data quality and scope note**
   - Purpose: state what the dashboard can and cannot prove.
   - Required visible note: period grain, unit of measure, whether plan/yield/OEE/defect fields exist, and normalization assumptions.

## Interaction Model

- Filters: period, line, shift, product, machine.
- Drill-down dimensions: line -> machine -> shift; defect type -> station.
- Comparison controls: current vs previous period; actual vs plan when fields exist.
- Tooltip content: output, yield %, OEE component, defect count, comparison value.
- Export/download behavior: dashboard PDF export and individual chart download.
- Theme behavior: page-level theme switch that updates all surfaces and charts.

## Geographic Rules

- City/site field detection: use metadata, field names, and sample values (e.g., output by plant/site).
- Metric selection: prefer output, then yield.
- When triggered, read `workflow_specs/dashboard_modules/city_sales_map.md`.
- Fallback when coordinates or map coverage are insufficient: visible data-gap card + site/line ranking bar.

## Diagnostic Modules

- Cross-analysis matrix: line/machine x shift, product x yield, defect type x station, OEE component x line.
- Anomaly scan: output falling with yield stable (downtime) or yield falling with output stable (quality); defect spike on one line/shift/lot; single-component OEE loss.
- Attribution path: output change -> availability/performance/yield/mix -> line -> machine/shift.
- Data-gap cards: missing plan, missing yield inputs, missing OEE components, missing defect types.

## Layout Guidance

- Header and title rules: title must come from prompt/table/fields; stay domain-neutral when industry is unproven.
- KPI row: 4-5 cards (output vs plan, first-pass yield, OEE, defect rate).
- Primary charts row: output trend vs plan + yield/defect breakdown.
- Segment row: OEE components + defect Pareto.
- Diagnostic row: downtime by cause + anomaly/attribution + data quality note.
- Responsive behavior: preserve chart heights and avoid cards inside cards.

## Chart Recipe Requirements

- Trend: `references/examples/line-simple.md`
- Ranking/contribution: `references/examples/bar-simple.md`
- Pareto: Pareto bar recipe from `references/examples/INDEX.md`.
- Cross-analysis: heatmap or grouped bar from `references/examples/INDEX.md`.
- Map: `workflow_specs/dashboard_modules/city_sales_map.md` then `references/examples/geo-map-scatter.md`
- Fallback: `references/examples/bar-simple.md`

## Validation Checklist

- Title is traceable to prompt/table/fields.
- At least 6 analytical modules are present when data supports them.
- Triggered site/city map module is present or has explicit fallback.
- Every chart cites its recipe context.
- Dashboard includes business interpretation cards, not only charts.
- No unsupported KPI or industry concept is invented; do not report plan attainment, yield, full OEE, or defect Pareto without the required fields.
