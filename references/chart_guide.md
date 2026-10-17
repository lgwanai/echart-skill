# Reliable chart generation

Use `scripts/chart_builder.py` for bar, column, line, area, stacked_bar,
stacked_area, scatter, pie and mixed. Choose the analysis and layout yourself;
the compiler owns data serialization, options, offline library order, responsive
sizing, accessibility and matching source tables. Do not edit compiled JavaScript.

## Input

Reference actual row-oriented query-result JSON, relative to the spec file:

```json
{"charts":[{
  "id":"revenue_trend","view":"line","title":"Monthly revenue",
  "scope":"Completed calendar months; SUM(net_revenue); CNY",
  "source":"query q1, fact_sales","query_hash":"<actual query hash>",
  "rows_path":"query_results/monthly.json","x":"month","x_order":"explicit",
  "metrics":[{"field":"revenue","name":"Revenue","unit":"CNY"}]
}]}
```

| Intent | View | Contract |
|---|---|---|
| Rank / magnitude | bar / column | Unique categories, one row per category |
| Ordered trend | line / area | SQL-sorted order; x_order=explicit; null stays a gap |
| Composition | stacked_bar / stacked_area | Wide table, all series in the same unit |
| Two metrics | mixed | Exactly two metrics with type bar then line; independent y-axes |
| Relationship | scatter | Numeric x/y; one y metric and explicit x_unit |
| Approximate share | pie | 2–3 strictly positive categories and one metric |

Numeric strings, bool, NaN, infinity, numbers above JS-safe magnitude, all-null metrics, duplicate categories and
unknown views fail before output. No implicit aggregation, sorting, truncation,
unit conversion or null-to-zero conversion. Correct periods and metric definitions
remain the analysis workflow's responsibility.

## Build and verify

```bash
python scripts/chart_builder.py chart-spec.json --output outputs/chart.html --evidence evidence-draft.json
# Optional: --shell layout.html containing exactly one <!-- ECHART_CHARTS -->
```

Section-aware shells may instead contain exactly one `<!-- ECHART_CHART:<id> -->`
per chart; mixing global/named slots, duplicate or missing slots fails. For
reports, first run `project_report.py resolve`, then use `project_report.py build`
with the plan, evidence and project preferences (see report workflow). The
generator owns these named slots; a project shell only supplies REPORT_CONTENT.
Dashboard specs similarly route through `project_dashboard.py resolve/build`,
using the independent `config/dashboards/` registry and DASHBOARD_CONTENT shell
marker. The project compiler owns KPI evidence, section placement and runtime.

With `--evidence`, the builder binds the manifest, runs all delivery gates including
the real browser, then atomically publishes the output. Failure does not overwrite
an existing deliverable. Without `--evidence`, it produces a draft only; bind and run
`validate_delivery.py` before delivery. Evidence draft format is defined in
`workflow_specs/artifact_evidence_contract.md`; non-temporal queries omit date_field,
but comparisons require usable dates on both sides.

Use the appropriate dashboard/report workflow
shell for narrative, generation time, limitations, comparison labels and contracts.
Keep `chart-build-spec` and `data-echart-chart`: the browser verifies every expected
instance, series data, axes, render surface and desktop/mobile layout.
Inspect a screenshot for meaningful labels/legends; runtime checks do not prove
business conclusions. Browser unavailable means unverified, never a success claim.

## Specialized views

Maps, 3D, sankey, waterfall and custom series use the optional historical archive:

```bash
python scripts/reference_assets.py search "sankey" --limit 3
python scripts/reference_assets.py get sankey-simple
```

Historical demos are reference material, not certified production templates.
Their demo data, network dependencies and bracket-counting replacement instructions
are superseded by this guide. Do not splice data arrays by regex/bracket counting.
Mark every custom container `data-echart-chart`, provide local assets and run the
same evidence and delivery checks. If an optional recipe is missing, obtain the
full package; never silently substitute a chart with different analytical meaning.

The legacy `report_engine.py` also reads historical recipes and requires the full
package. The portable workflow uses the compiler and agent-authored report shell.
