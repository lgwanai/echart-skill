# Analysis Expression Quality Contract

Use this contract before choosing an ECharts recipe for `/chart`, `/dashboard`,
`/analyze`, `/insight`, or `/report`. It is a blocking quality gate, not optional
writing advice.

## 1. Plan the message before the visual

Use the fixed sequence **Message → Relation → View**.

For every analytical view, decide in this order:

1. **Message** — write one complete, evidence-backed conclusion sentence.
2. **Relation** — identify the relationship the evidence must communicate.
3. **View** — choose the most accurate visual encoding for that relationship.
4. **Table mode** — decide whether exact values need a visible companion table.
5. **Next check** — state which query would confirm or refute the explanation.

A title such as `销售趋势`, `地区分析`, or `产品占比` names a topic but says
nothing. Prefer a conclusion such as `华东销售额连续三月下降，6 月较峰值低 18%`.

Every plan must be saved as JSON and pass:

```bash
python scripts/validate_analysis_plan.py <analysis-plan.json>
```

Do not generate the final chart/report/dashboard until the plan passes.

## 2. Relationship-to-view matrix

| Relationship | Best default | Useful alternatives | Avoid by default |
|---|---|---|---|
| Single value | KPI + short sentence | compact table | decorative gauge |
| Deviation / target gap | diverging bar, bullet, waterfall | slope, line | pie |
| Correlation | scatter | bubble, linked scatter, small multiples | dual-axis line used as proof |
| Ranking | sorted horizontal bar | lollipop, bump, table | unsorted vertical bars |
| Distribution | histogram, boxplot | violin, strip, table | bar of aggregates presented as distribution |
| Time / change | line | column, slope, calendar heatmap, small multiples | pie |
| Magnitude | sorted bar | paired bar, column, table | area/volume encodings |
| Composition | sorted bar or 100% stacked bar | treemap, stacked area | pie when categories exceed 3 |
| Spatial | map plus ranked-bar fallback | effect scatter, choropleth | map when location is not analytical |
| Flow / conversion | Sankey, funnel | graph, flow map | disconnected KPI cards |

Prefer common-position and length encodings over angle, area, volume, or color
intensity. A pie chart is allowed only for 2–3 categories when approximate share
is the sole message. Use a sorted bar when users must compare close values.

Derived metrics must retain their baseline layer: show the absolute value beside
share, change, rate, index, or contribution. Never show only a percentage when
the underlying volume changes the decision.

## 3. Chart and table are different tools

The existing `查看数据` table is an audit/source toggle behind every chart. It
does not replace an analytical table. Set one of these modes for each view:

- `source_toggle`: chart is sufficient for pattern recognition; exact values are
  available through the required hidden source-data table.
- `companion`: chart communicates the pattern and a visible compact table supports
  lookup, comparison, or action.
- `primary`: table or KPI is the main expression; a chart would add noise.

Use `companion` or `primary` when any condition applies:

- the user needs exact lookup, reconciliation, or row-level action;
- there are more than 15 categories;
- four or more measures must be compared together;
- the output is an exception, outlier, risk, forecast-range, or action list;
- a ranking decision needs value, share, change, sample size, or owner together;
- every visual mark would otherwise need a data label.

A companion table should be selective: include decision columns, sort by the
decision metric, highlight exceptions, and avoid dumping the source dataset.

## 4. Deep-analysis ladder

Every major finding must complete all six fields:

1. **What** — what changed, where, and by how much?
2. **Baseline** — compared with which period, target, peer, or distribution?
3. **Why status** — `tested`, `hypothesis`, or `unknown`.
4. **Why** — tested drivers, or clearly labelled hypotheses; never invent causes.
5. **So what** — business impact or decision implication.
6. **Next check** — the next concrete query/segmentation needed to verify the cause.

It must also cite evidence and state limitations. Descriptive detectors such as
ranking, trend, anomaly, or correlation produce candidates, not finished causal
conclusions. For a major finding, execute at least one relevant next check when
the fields exist; otherwise expose the data gap.

Useful drill-down sequence:

```text
total change
  -> contribution by primary dimension
  -> split leading positive/negative segments by a second dimension
  -> volume × rate/price decomposition where supported
  -> anomaly and data-quality check
  -> stability across periods / sample-size check
```

Correlation is never causal proof. Seasonality requires multiple comparable
cycles. Incomplete periods must be labelled or excluded from period comparison.

## 5. Period alignment is a blocking gate

Any view that says 同比, 环比, 同期, 对比, YoY, QoQ, MoM, WoW, or `vs` must declare a
`comparison` object in the analysis plan. A footnote cannot make an invalid
comparison acceptable.

- First query the maximum available business date and determine the latest
  **complete** day/week/month/quarter.
- Default to complete periods: if the current year has complete data through
  July, compare January–July with January–July of the baseline year.
- Current partial month versus prior full month/year is forbidden. A partial
  window is allowed only when both sides use the same elapsed days and the title
  says it is partial.
- KPI, chart, ranking, table, attribution, and price comparison SQL must reuse
  the same boundaries. Never fix only the headline KPI.
- For YoY, start and end month/day must match and the years must be exactly one
  year apart when using the standard calendar.
- Do not assume every organization uses calendar months. Declare `calendar` as
  `calendar`, `fiscal`, `retail_445`, or `custom`. Fiscal, 4-4-5 retail, and
  custom calendars must align governed named periods (`same_named_periods`) or
  the same elapsed days; provide `current_period_key` and
  `baseline_period_key` for named-period alignment.
- These rules are metric- and industry-neutral: they apply equally to revenue,
  expenses, margin, inventory, traffic, orders, headcount, risk, and any other
  period-based measure.

Required comparison fields:

```json
{
  "type": "yoy",
  "calendar": "calendar",
  "current_start": "2026-01-01",
  "current_end": "2026-07-31",
  "baseline_start": "2025-01-01",
  "baseline_end": "2025-07-31",
  "current_period_status": "complete",
  "baseline_period_status": "complete",
  "latest_complete_period_end": "2026-07-31",
  "alignment": "same_complete_periods",
  "comparable": true
}
```

Non-calendar example:

```json
{
  "type": "yoy",
  "calendar": "retail_445",
  "current_period_key": "FY2026-P07",
  "baseline_period_key": "FY2025-P07",
  "current_start": "2026-07-05",
  "current_end": "2026-08-01",
  "baseline_start": "2025-07-06",
  "baseline_end": "2025-08-02",
  "current_period_status": "complete",
  "baseline_period_status": "complete",
  "latest_complete_period_end": "2026-08-01",
  "alignment": "same_named_periods",
  "comparable": true
}
```

The final HTML is independently auditable and must not rely only on the sidecar
analysis plan. If visible page text contains 同比, 环比, 同期, YoY, QoQ, MoM, or WoW, embed:

```html
<script type="application/json" id="analysis-comparison-contract">
{
  "version": 1,
  "comparisons": [{
    "type": "yoy",
    "calendar": "calendar",
    "current_start": "2026-01-01",
    "current_end": "2026-07-31",
    "baseline_start": "2025-01-01",
    "baseline_end": "2025-07-31",
    "current_period_status": "complete",
    "baseline_period_status": "complete",
    "latest_complete_period_end": "2026-07-31",
    "alignment": "same_complete_periods",
    "comparable": true,
    "current_label": "2026年1–7月",
    "baseline_label": "2025年1–7月"
  }]
}
</script>
```

`current_label` and `baseline_label` must both appear in visible page text. Run
`python scripts/validate_delivery.py <output.html>` as the final blocking gate. It
reuses the same date-alignment validator as the plan gate, so YTD-versus-full-
year cannot pass merely because an Agent skipped or detached the plan file.

## 6. Plan schema

```json
{
  "decision_context": "决定下月区域资源调整",
  "audience": "销售负责人",
  "analysis_mode": "decision_support",
  "questions": ["哪些区域贡献了本月下滑？"],
  "views": [{
    "id": "v1",
    "message": "华东贡献本月销售额下滑的 62%",
    "relation": "deviation",
    "primary_view": "waterfall",
    "reason": "需要表达各区域对总变化的正负贡献",
    "rejected_alternatives": [{"view": "pie", "reason": "无法表达负贡献"}],
    "table_mode": "companion",
    "table_reason": "负责人需要核对区域贡献额和贡献率",
    "table_columns": ["区域", "销售额变化", "贡献率"],
    "category_count": 8,
    "exact_lookup": true,
    "measure_count": 2,
    "evidence_ref": "Data A3",
    "comparison": {
      "type": "yoy",
      "current_start": "2026-01-01",
      "current_end": "2026-07-31",
      "baseline_start": "2025-01-01",
      "baseline_end": "2025-07-31",
      "current_period_status": "complete",
      "baseline_period_status": "complete",
      "latest_complete_period_end": "2026-07-31",
      "alignment": "same_complete_periods",
      "comparable": true
    }
  }],
  "findings": [{
    "id": "f1",
    "importance": "major",
    "what": "销售额环比下降 12%，华东贡献 62% 的降幅",
    "baseline": "与上月同口径完整周期比较",
    "why_status": "hypothesis",
    "why": "订单量下降是当前优先假设，尚需渠道与库存数据验证",
    "so_what": "资源应优先用于华东问题定位，而不是全局调价",
    "next_check": "按华东渠道拆分订单量、客单价和库存可用率",
    "evidence_refs": ["Data A1", "Data A3"],
    "limitations": ["当前数据不含投放和库存字段"]
  }]
}
```

## 7. Delivery gate

Before returning an artifact, confirm:

- every view has a conclusion title and an explicit relationship;
- chosen visual is permitted for the relationship and rejected alternatives are recorded;
- baseline quantities accompany derived metrics;
- every period comparison uses aligned boundaries and does not exceed the latest complete period;
- table mode is intentional and visible companion tables are used when triggered;
- every major finding completes What → Baseline → Why → So what → Next check;
- evidence references and limitations are present;
- the analysis plan and the final HTML validators both pass.
