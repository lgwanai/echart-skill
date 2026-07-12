# Supply Chain & Procurement Dashboard Expert

Use this dashboard expert for procurement and supply-chain operating surfaces: spend, supplier performance, on-time delivery, inventory turnover, price/quote comparison, and sourcing risk.

## Dashboard Mission

Create a procurement operating surface that shows where spend goes, whether cost change is price- or volume-driven, how suppliers perform on delivery and quality, where concentration risk sits, and whether inventory is healthy. The target user is a procurement or supply-chain manager who must decide where to renegotiate, dual-source, or reduce stock.

## Required Modules

1. **KPI summary**
   - Purpose: show total spend, price vs volume delta, on-time rate, and inventory turnover at a glance.
   - Data needed: spend fields; baseline period for deltas.
   - Card: KPI cards with value, delta vs baseline, and scope note.

2. **Spend trend and structure**
   - Purpose: show spend direction and composition by category/supplier.
   - Data needed: date + spend; category/supplier dimension.
   - Chart recipe: `references/examples/line-simple.md` for trend, `references/examples/bar-simple.md` for structure.

3. **Price vs volume decomposition (cross-analysis)**
   - Purpose: separate price effect from volume effect on spend change.
   - Data needed: quantity + unit price or spend per item/period.
   - Chart recipe: waterfall (`bar-waterfall`) or grouped bar from `references/examples/INDEX.md`.

4. **Supplier scorecard**
   - Purpose: rank suppliers on delivery, quality, and price.
   - Data needed: supplier + on-time/quality/price metrics.
   - Chart recipe: `references/examples/bar-simple.md` or radar from `references/examples/INDEX.md`.

5. **Supplier concentration / single-source risk**
   - Purpose: expose dependency on few suppliers for critical items.
   - Data needed: spend share by supplier; item criticality if available.
   - Chart recipe: `references/examples/pie-simple.md` or Pareto bar.

6. **Inventory turnover and slow-moving stock**
   - Purpose: flag excess and dead stock.
   - Data needed: inventory balance + movement/turnover; aging if available.
   - Module: turnover bar + slow-moving table; skip with a visible data-gap card if fields are absent.

7. **Data quality and scope note**
   - Purpose: state what the dashboard can and cannot prove.
   - Required visible note: period grain, currency, whether quantity/delivery/quality/inventory fields exist, and item-matching assumptions.

## Interaction Model

- Filters: period, category, supplier, department/requester, region.
- Drill-down dimensions: category -> item -> supplier; supplier -> on-time/quality.
- Comparison controls: current vs previous period when a date field exists.
- Tooltip content: spend, unit price, share, on-time %, comparison value.
- Export/download behavior: dashboard PDF export and individual chart download.
- Theme behavior: page-level theme switch that updates all surfaces and charts.

## Geographic Rules

- City field detection: use metadata, field names, and sample values (e.g., spend/supplier by city).
- Metric selection: prefer spend, then on-time rate.
- When triggered, read `workflow_specs/dashboard_modules/city_sales_map.md`.
- Fallback when coordinates or map coverage are insufficient: visible data-gap card + region/supplier ranking bar.

## Diagnostic Modules

- Cross-analysis matrix: item/category x supplier, time x price vs volume, supplier x on-time x quality.
- Anomaly scan: price-driven spend rise, unit-price dispersion, delivery reliability drop, single-source concentration, turnover fall.
- Attribution path: spend change -> price/volume/mix/supplier-switch -> item -> supplier.
- Data-gap cards: missing quantity, missing delivery dates, missing quality, missing inventory.

## Layout Guidance

- Header and title rules: title must come from prompt/table/fields; stay domain-neutral when industry is unproven.
- KPI row: 4-5 cards (total spend, price/volume delta, on-time rate, inventory turnover).
- Primary charts row: spend trend + price-vs-volume decomposition.
- Segment row: supplier scorecard + concentration risk.
- Diagnostic row: inventory turnover/slow-moving + anomaly/attribution + data quality note.
- Responsive behavior: preserve chart heights and avoid cards inside cards.

## Chart Recipe Requirements

- Trend: `references/examples/line-simple.md`
- Ranking/contribution: `references/examples/bar-simple.md`
- Structure: `references/examples/pie-simple.md` or bar fallback.
- Decomposition: waterfall (`bar-waterfall`) from `references/examples/INDEX.md`.
- Map: `workflow_specs/dashboard_modules/city_sales_map.md` then `references/examples/geo-map-scatter.md`
- Fallback: `references/examples/bar-simple.md`

## Validation Checklist

- Title is traceable to prompt/table/fields.
- At least 6 analytical modules are present when data supports them.
- Triggered city map module is present or has explicit fallback.
- Every chart cites its recipe context.
- Dashboard includes business interpretation cards, not only charts.
- No unsupported KPI or industry concept is invented; do not report on-time performance, price/volume split, or inventory turnover without the required fields.
