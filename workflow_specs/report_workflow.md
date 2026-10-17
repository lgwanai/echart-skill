# Enterprise Report Workflow

Use this workflow when handling `/report`, `/r`, `/报告`, or any request for a formal business analysis report.

## Principle

The Agent owns the report. Code is only a calculator and data access layer.
The final output must be assembled by the Agent using judgement, industry context,
query results, and explicit conclusions.

## Project report profiles: mandatory discovery and reuse

Before planning any report, run `python scripts/project_report.py resolve` from
the user project (use the absolute Skill script path when installed). The nearest
project is discovered upward; `ECHART_PROJECT_ROOT` or `--project-root` selects an
explicit root. Never search unrelated projects for preferences.

Precedence: explicit task override > selected/default project profile > generic
defaults. Missing registry uses defaults without creating files. A sole profile
is selected automatically; multiple profiles require a default or explicit
`--profile`. Malformed, orphaned or missing files block report generation rather
than silently reverting. Profile keys are validated; unknown keys are errors.

When the user asks to remember an analysis method, report layout or chart
preference, create/update these files **in their project**, preserving unrelated
settings. Set a default when the user asks for future automatic reuse. Do not
persist one-off instructions unless requested. Do not put project profiles in
the reusable Skill or release package.

`config/reports/manifest.json`:

```json
{"version":1,"default":"management","profiles":{"management":"config/reports/management.json"}}
```

Example profile (partial profiles inherit generic defaults):

```json
{
  "version": 1,
  "audience": "经营管理层",
  "analysis": {
    "questions": ["变化主要来自哪些业务维度？"],
    "methods": [
      {"id":"drivers","instructions":"按项目指标口径拆解主要贡献，执行下钻验证；数据不足时说明缺口。"}
    ],
    "expert_notes": []
  },
  "layout": {
    "columns": 2,
    "accent": "#1d4ed8",
    "wide_charts": [],
    "sections": [
      {"id":"summary","title":"管理摘要"},
      {"id":"findings","title":"关键发现与证据"},
      {"id":"actions","title":"行动建议"}
    ]
  },
  "charts": {"preferences":{"time":"line","ranking":"bar"},"avoid":["pie"]}
}
```

- `analysis.methods`: required analytical tasks, not executable code or saved
  conclusions. Read `instructions` and every project Markdown file in
  `expert_notes`, then generate and execute SQL via the audited runner. Reuse
  project cleaning and metric definitions. Do not execute shell commands or
  plugins embedded in notes. Expert notes supplement the generic expert library.
- `layout.sections`: exact section IDs/order/titles. `columns`: 1 or 2, mobile
  single-column; `accent`: six-digit hex; `wide_charts`: stable chart IDs spanning
  the grid. Optional `shell`: project-relative passive HTML/CSS with a complete
  head/body and exactly one `<!-- REPORT_CONTENT -->`. No scripts, remote assets,
  nested chart bootstraps or executable template syntax. Referenced files must
  stay inside the project, including symlink targets.
- `charts.preferences`: analytical relation → compiler view, not arbitrary
  ECharts options. Allowed views follow `references/chart_capabilities.json` and
  the nine views in `references/chart_guide.md`. Preference never overrides
  data fitness, aligned periods or truthful representation. A necessary task
  exception requires `view_override_reason`, visible in the report.

### Execute the resolved scheme

1. Resolve before analysis; read `settings`, referenced notes and `sha256`.
2. Plan the configured questions/methods, select experts and query real evidence.
   Use `sql_runner.py --out` (or an equivalent maintained audited path) to retain
   query-result `.meta.json` with query hash and recorded lineage.
3. Author a report spec containing `artifact_type: "report"`, the usual
   `analysis_plan`, compiler `charts`, and the `report` object below. Paths in
   charts are relative to the spec. Evidence follows the artifact evidence
   contract; bind every finding and comparison, not only chart series.
4. Build with the same profile/overrides used to resolve. The generator checks
   analytical coverage, applies layout/view preferences, binds the evidence and
   runs the complete delivery gate including desktop/mobile browser checks.
   Failure leaves an existing report unchanged. Config, expert-note or shell
   changes invalidate the planning hash: resolve and re-plan, never just replace
   the hash without reviewing the change.

Report object shape (illustrative IDs; supply actual content and query IDs):

```json
{
  "title":"经营分析报告",
  "scope":"实际数据范围、日期粒度、指标单位及筛选条件",
  "limitations":["实际数据局限"],
  "profile_sha256":"<resolve 返回的 sha256>",
  "sections":[
    {"id":"summary","paragraphs":["有证据支持的结论"],"evidence_query_ids":["q1"]},
    {"id":"findings","paragraphs":["观察、解释及不确定性"],"evidence_query_ids":["q1"]},
    {"id":"actions","paragraphs":["与证据相符的行动建议"],"evidence_query_ids":["q1"]}
  ],
  "methods":[
    {"id":"drivers","status":"executed","evidence_query_ids":["q1"],"note":"实际执行了什么、结果与限制"}
  ]
}
```

Each chart adds `section` matching a configured section ID. Chart IDs must match
plan view IDs. `view` may be omitted to apply the relation preference; the
analysis plan's `primary_view` must agree. Companion tables use the plan's
`table_columns` and `table_reason` and are rendered from the real query rows.
Every configured method needs `executed` with nonempty valid query IDs, or
`data_gap` with a visible reason (empty evidence allowed). Never mark a method
executed merely because a related query exists: review that the SQL actually
implements it. Automated gates verify coverage, references and chart data, not
the semantic truth of every interpretation or causal claim.

```bash
python /path/to/echart-skill/scripts/project_report.py --project-root /path/to/project resolve
python /path/to/echart-skill/scripts/project_report.py --project-root /path/to/project build outputs/report-spec.json --evidence outputs/evidence.json --output outputs/report.html
# Optional global arguments, before resolve/build:
# --profile management --overrides outputs/task-report-overrides.json
```

Overrides use profile keys except `version`; objects merge, lists replace.
They are never written back. `chart_builder.py` delegates specs with `report` or
`artifact_type: "report"` to this same gated path. Legacy `ReportEngine.generate`
refuses to bypass an existing project registry.

The current compiler path requires at least one supported chart. Table-only,
specialized charts or non-HTML formats need a separately verified workflow;
disclose this limit, still load the scheme, and do not claim that unimplemented
layout/preferences were applied. Project preferences never disable evidence,
period-alignment, cleaning or delivery gates.

## Required Steps

1. **Clarify the business surface**
   - Infer likely industry from user wording, table name, file name, column names, and sample values.
   - If ambiguous, state the assumed industry in the report and mark confidence.
   - Do not rely on hardcoded Python industry classifiers.

2. **Select experts dynamically**
   - Read `workflow_specs/expert_library/INDEX.md`.
   - Select one primary expert and optional supporting experts.
   - Read every selected expert Markdown file completely before making the analysis plan.
   - Record selected experts and confidence in the report notes or appendix.
   - Do not encode expert selection or expert rules as Python if/else logic.

3. **Build an analysis plan before writing**
   - Read `workflow_specs/analysis_expression_quality.md` completely.
   - Save message/relation/view/table/finding decisions as an analysis-plan JSON and run `python scripts/validate_analysis_plan.py <plan.json>` before selecting recipes or writing the report.
   - Query the maximum available business date and latest complete period. Every YoY/MoM branch must reuse the same aligned dates across headline metrics, charts, tables, attribution, and narrative.
   - Use the selected expert files as the analysis playbook.
   - Decide which views are supported by available data.
   - List unsupported views as data gaps instead of fabricating conclusions.
   - Build a pyramid storyline before writing: top conclusion, supporting findings, evidence charts, appendix data.
   - Plan multiple finding branches. Each finding branch must also follow pyramid logic internally: local conclusion, supporting observations, evidence chart, attribution explanation, action.
   - Assign appendix data table IDs before writing, e.g. `A1`, `A2`, `A3`. Every major conclusion and finding must cite at least one appendix table ID.
   - Extract and execute each selected expert file's `Cross Analysis Matrix`, `Anomaly Patterns`, and `Deep Attribution Paths`.

4. **Use local tools only for evidence**
   - Use DuckDB/SQL/Python for profiling, grouping, period comparison, anomaly scan, and attribution math.
   - Use existing engines such as `insight_engine.py`, `attribution_engine.py`, and `forecast_engine.py` only as evidence providers.
   - The Agent writes the interpretation, not the tool.
   - Choose chart, chart + visible companion table, or table-first expression using `analysis_expression_quality.md`. The hidden `查看数据` table is only an audit source toggle, not the analytical companion table.
   - At minimum, collect evidence for baseline comparison, anomaly scan, cross-analysis, and driver attribution when data supports them.
   - Do not expose SQL in the main report body. Translate calculation logic into plain business wording.

5. **Write conclusion-first**
   - Start with 3-5 business conclusions.
   - Each conclusion should answer: what happened, why it likely happened, what to do next.
   - Include numbers and comparison periods when available.
   - Follow global pyramid writing: conclusion -> findings -> chart evidence -> attribution explanation -> action -> appendix data.
   - Each finding must also follow local pyramid writing: finding conclusion -> observation -> chart evidence -> attribution -> local action.
   - Key conclusions and finding conclusions must cite appendix data tables, such as `[Data A1]` or `[Data A2, A4]`.
   - Every analysis module and every finding branch must include a short "统计口径说明" in plain language: data range, date grain, metric definition, grouping dimension, filters, and limitations. Do not show SQL.
   - Do not write a data dump, metric inventory, or table-by-table commentary.

6. **Generate the final artifact**
   - Use the project-report generation path above for supported HTML reports. It supplies a responsive, print-friendly shell or loads the resolved project shell. The legacy `workflow_specs/html_templates/report_light.html` is a reference for separately verified custom reports, not an override of project preferences.
   - Use `workflow_specs/visual_templates/light.md` or `dark.md` only as visual direction; do not use Markdown visual notes as the final HTML shell.
   - Generate long reports section by section: cover, one-page conclusions, each finding branch, chart evidence, attribution, actions, appendix.
   - Assemble the section outputs into one unified HTML report only after all branches are complete and internally consistent.
   - Markdown report: suitable for direct reading or document conversion.
   - HTML report: standalone, enterprise/PDF-like layout, no external dependencies.
   - JSON report: only when user explicitly needs structured data; include evidence and conclusions.

## Enterprise Report Structure

Use this pyramid structure unless the user asks otherwise:

1. 封面：报告主题、分析对象、周期、口径、专家模式
2. 一页纸结论：3-5 条核心结论，每条包含影响、原因判断、建议动作、数据引用
3. 关键发现分支：按业务重要性排序；每个分支内部遵守“局部结论 -> 发现 -> 图表举证 -> 解释归因 -> 行动建议”
4. 图表举证：每个关键发现必须配一个主图表和一句证据解释
5. 归因与异常：解释变化来自哪里、异常出现在哪里、是否可行动
6. 行动建议：按优先级列出下一步动作、预期影响、所需数据
7. 附录数据：汇总所有分支用到的数据表、SQL、字段口径、缺失数据、详细样本，并提供可引用编号

Forbidden report structures:

- 先介绍大量背景，再把结论放到最后。
- 直接罗列数据表、字段画像或统计量，缺少业务判断。
- 用表格替代举证图表。
- 按工具输出顺序拼接 insight/forecast/attribution 文本。
- 前文结论没有引用附录数据表。
- 关键发现只列标题，没有内部结论、图表证据和归因解释。

## Pyramid Writing Contract

The whole report must follow this global pyramid:

1. **Top conclusion**: 3-5 board-level conclusions.
2. **Finding branches**: multiple branches that support the top conclusions.
3. **Evidence charts**: charts that prove each branch.
4. **Attribution explanation**: why the evidence likely happened.
5. **Actions**: what to do next.
6. **Appendix data**: all data tables used by the branches.

Every finding branch must follow this local pyramid:

1. **Conclusion**: one sentence that a business owner can act on.
2. **Finding**: 2-3 supporting observations with exact numbers.
3. **Evidence chart**: line/bar/funnel/waterfall/heatmap/scatter/map as appropriate.
4. **Interpretation**: why this likely happened and what uncertainty remains.
5. **Action**: recommended business response.
6. **Data reference**: cite appendix table IDs that support the conclusion.

Example:

- Conclusion: `6 月 GMV 下滑主要由华东渠道订单数下降驱动，客单价不是主因。[Data A1, A3]`
- Finding: `华东贡献了总下滑的 62%，订单数环比 -18%，AOV 仅 -1.7%。`
- Evidence chart: waterfall for regional contribution + line chart for order trend.
- Action: `优先排查华东渠道投放、库存和履约，而不是全站调价。`

## Appendix Data Citation Contract

All evidence tables used in the report must be collected in the appendix and assigned stable IDs:

- `A1`: executive KPI summary and period comparison.
- `A2`: trend data used by line/area charts.
- `A3`: contribution or attribution data used by waterfall/bar charts.
- `A4`: cross-analysis data used by heatmaps, segmented bars, scatter plots, or matrices.
- `A5+`: additional expert-specific evidence tables.

Citation rules:

- Every top conclusion must cite one or more appendix tables.
- Every finding branch conclusion must cite one or more appendix tables.
- Every chart must cite the appendix table it was generated from.
- Appendix tables must include enough rows/columns to reproduce the claim or chart.
- Do not place large evidence tables in the main body; show a compact cited snippet only when it improves readability.

## Expert Library

Expert playbooks live in `workflow_specs/expert_library/`.

The Agent must not summarize from memory when an expert is selected. It must read
the selected expert file and follow its mission, required analysis views, required
data checks, cross analysis matrix, anomaly patterns, deep attribution paths,
core metrics, report questions, and dashboard modules.

When multiple experts apply, use a primary/supporting structure:

- Primary expert decides the report storyline and main KPI tree.
- Supporting experts add risk, quality, finance, campaign, product, or customer angles.
- Conflicts are resolved by the user’s stated objective and available evidence.

## Evidence Rules

- Every strong conclusion needs at least one number, comparison, rank, or contribution statement.
- Every strong conclusion and every finding branch conclusion needs an appendix data citation.
- Every claim must respect the actual fields and data supplied by the user.
- Do not invent business concepts that are not present in the data or user instruction. For example, do not mention target achievement rate, budget variance, SLA compliance, retention, funnel conversion, profit margin, or ROI unless the required fields or user-provided definitions exist.
- Every report must attempt the mandatory expert reasoning loop from `expert_library/INDEX.md`.
- Every selected primary expert must produce:
  - one baseline comparison
  - one anomaly scan
  - one cross-analysis
  - one attribution/drill-down path
- Every key finding needs the strongest evidence view. Prefer a chart for patterns; use chart + compact visible table for precise decision lookup, and table-first when a chart adds noise.
- Choose chart types by analytical purpose:
  - Trend/change: line or area chart.
  - Ranking/contribution: bar chart or waterfall.
  - Funnel loss: funnel chart.
  - Retention/cohort: heatmap.
  - Relationship: scatter chart.
  - Geographic distribution: map with bar fallback.
  - City transaction distribution: when a city field and transaction amount/sales amount/GMV field are both present, add a city transaction map. Use `geo + effectScatter` or a province/city map recipe; do not force city data into province totals unless province mapping exists.
  - Structure: treemap, stacked bar, or pie only when categories are few.
- If evidence is weak, phrase as “初步判断” or “需要补充数据验证”.
- Every major finding must complete What, baseline, Why status, Why, So what, next check, evidence references, and limitations. Execute at least one next check when fields exist; otherwise expose the data gap.
- When discussing seasonality or external factors, do not assert causality from internal data alone. Prefer wording such as: `补充节假日、活动投放、价格、库存、天气、渠道策略等数据后，可以进一步判断这是季节性波动还是外部因素导致。`
- Do not overfit one chart. Reports must include interpretation and action.
- Do not hide data limitations.

## Statistical Scope Contract

Each report module must show the necessary statistical scope in conversational language:

- Data range: which table/file, row count, date range if available.
- Date grain: daily, weekly, monthly, order-level, user-level, transaction-level, or "no date field available".
- Metric scope: which numeric field is summed, averaged, counted, or compared.
- Grouping scope: which dimension fields are used for ranking, segmentation, or cross-analysis.
- Filter scope: any user-provided filter, period, segment, or cleaning rule.
- Limitation: what the current data cannot prove.

The main report should say this as a reader-facing explanation, for example:

`统计口径说明：本模块基于订单表中 12,430 条记录，按 order_date 观察每日变化，金额口径为 amount 汇总，分组优先看 region 和 channel。当前数据没有投放、节假日和库存字段，因此不能直接判断波动是否由外部因素导致。`

Do not display SQL in the main body. SQL can only appear in the appendix when the user asks for audit detail.

## HTML Report Visual Rules

- Apply the resolved project layout and generator shell; use `workflow_specs/html_templates/report_light.html` as visual reference for separately verified custom reports.
- Read `workflow_specs/visual_templates/light.md` by default as supplemental visual direction.
- Read `workflow_specs/visual_templates/dark.md` only when the user asks for dark mode, then adapt the HTML shell tokens without weakening the PDF-like structure.
- The HTML should look like an enterprise PDF: paper-like page, formal header, numbered sections, compact tables, print-friendly CSS.
- The Agent may adapt layout and CSS to match the user’s brand or industry.
- The generated CSS must visibly implement the HTML shell: page background, paper canvas, typography scale, section rhythm, chart panels, table style, status colors, and print rules.
- If HTML looks like browser-default output, a plain Markdown conversion, or a loose table page, regenerate before returning.

## Chart Generation Contract

Before report assembly, read `workflow_specs/artifact_evidence_contract.md` and
bind the evidence files, metric/scope fingerprints, comparisons, charts, and
findings into the final HTML.

Every chart embedded in a report must use the maintained compiler or an explicitly verified specialized recipe:

1. Read `references/chart_guide.md` and choose the view by analytical meaning.
2. Common views use `scripts/chart_builder.py`. Specialized views use `scripts/reference_assets.py get <chart-name>` to read the archived recipe completely; `references/examples/<chart-name>.md` paths are virtual catalog identifiers, not loose files.
3. Query or calculate the exact evidence table that powers the chart.
4. Compile options from actual query-result JSON and explicit mappings. Never hand-copy data or splice arrays into example JavaScript.
5. Generate charts one by one. Do not assemble the report until each chart has a stable chart ID, selected recipe name, option, and appendix data reference.
6. Embed the full local `assets/echarts/echarts.min.js` library before any report chart bootstrap code. CDN scripts, local `<script src>`, runtime loaders, and placeholder ECharts stubs are invalid.
7. Project report assembly owns section-aware chart slots. Custom compiler shells use either one `<!-- ECHART_CHARTS -->` marker or exactly one `<!-- ECHART_CHART:<id> -->` per chart, never both. The builder injects `chart-build-spec` and isolated initialization; no duplicate bootstrap. For custom charts only, retain the `reportChartSpecs` path and mark every expected container `data-echart-chart`.
8. Keep ECharts JavaScript syntactically closed. In particular, `new echarts.graphic.LinearGradient(...)` and `new echarts.graphic.RadialGradient(...)` must close the constructor with `)` before closing the surrounding option object.
9. Cite the appendix data table ID used by the chart.
10. When the report visibly says 同比/环比/同期/YoY/QoQ/MoM/WoW, embed the version-1
    `analysis-comparison-contract` from `analysis_expression_quality.md`; its
    current/baseline labels must also be visible in the report.
11. Validate the generated HTML with `python scripts/validate_delivery.py <output.html>`. Evidence mismatch, browser/runtime failure, missing/malformed/misaligned period contract, external ECharts CDN, missing inlined ECharts library, or unclosed graphic constructor is blocking; repair and rerun before returning.

Do not rewrite compiler-owned code. If a specialized recipe/dependency is unavailable, obtain the full package or state the gap; never silently substitute a chart with different analytical meaning.
