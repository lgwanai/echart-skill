# Enterprise Report Workflow

Use this workflow when handling `/report`, `/r`, `/报告`, or any request for a formal business analysis report.

## Principle

The Agent owns the report. Code is only a calculator and data access layer.
The final output must be assembled by the Agent using judgement, industry context,
query results, and explicit conclusions.

## Required Steps

1. **Clarify the business surface**
   - Infer likely industry from user wording, table name, file name, column names, and sample values.
   - If ambiguous, state the assumed industry in the report and mark confidence.
   - Do not rely on hardcoded Python industry classifiers.

2. **Build an analysis plan before writing**
   - Select the industry playbook from the patterns below.
   - Decide which views are supported by available data.
   - List unsupported views as data gaps instead of fabricating conclusions.

3. **Use local tools only for evidence**
   - Use DuckDB/SQL/Python for profiling, grouping, period comparison, anomaly scan, and attribution math.
   - Use existing engines such as `insight_engine.py`, `attribution_engine.py`, and `forecast_engine.py` only as evidence providers.
   - The Agent writes the interpretation, not the tool.

4. **Write conclusion-first**
   - Start with 3-5 business conclusions.
   - Each conclusion should answer: what happened, why it likely happened, what to do next.
   - Include numbers and comparison periods when available.

5. **Generate the final artifact**
   - Markdown report: suitable for direct reading or document conversion.
   - HTML report: standalone, enterprise/PDF-like layout, no external dependencies.
   - JSON report: only when user explicitly needs structured data; include evidence and conclusions.

## Enterprise Report Structure

Use this default structure unless the user asks otherwise:

1. 封面与报告摘要
2. 分析结论
3. 行业专家分析框架
4. 数据与口径说明
5. 核心指标表现
6. 趋势与周期对比
7. 结构拆解
8. 异常扫描
9. 归因分析
10. 风险与机会
11. 行动建议
12. 附录：SQL/口径/数据限制

## Industry Playbooks

### Traffic / Growth

Required expert views:

- Scale: PV, UV, sessions, active users, new users
- Efficiency: CTR, conversion rate, bounce rate, visit depth
- Retention: D1/D7/D30 retention, cohort return, repeat visit
- Funnel: exposure, click, registration, order, payment or custom steps
- Attribution: channel, campaign, page, region, device, user segment

If retention or funnel columns are missing, explicitly write:

- `当前数据未包含留存字段，因此无法判断增长质量。`
- `当前数据未包含漏斗阶段字段，因此无法定位具体流失步骤。`

### Sales / E-commerce

Required expert views:

- Result: GMV, revenue, order count, quantity, AOV
- Structure: product, category, channel, region, customer type
- Comparison: MoM/YoY or latest period vs baseline
- Attribution: price, volume, mix, channel, region
- Quality: gross margin, refund, discount, inventory if available

### Finance / Management

Required expert views:

- Revenue, cost, expense, profit, margin
- Budget variance and period comparison
- Cost structure and department/project attribution
- Cash or receivable risk if available

### Customer / Membership

Required expert views:

- Acquisition, activation, retention, churn, repeat purchase
- Segment by member level, channel, region, lifecycle stage
- LTV or value contribution if available

### Operations / Fulfillment

Required expert views:

- Volume, timeliness, exception rate, inventory turnover
- Bottleneck by warehouse, region, carrier, product type
- Delay, shortage, backlog, cancellation if available

## Evidence Rules

- Every strong conclusion needs at least one number, comparison, rank, or contribution statement.
- If evidence is weak, phrase as “初步判断” or “需要补充数据验证”.
- Do not overfit one chart. Reports must include interpretation and action.
- Do not hide data limitations.

## HTML Report Visual Rules

- Use `workflow_specs/visual_templates/light.md` by default.
- Use `workflow_specs/visual_templates/dark.md` when the user asks for dark mode.
- The HTML should look like an enterprise PDF: paper-like page, formal header, numbered sections, compact tables, print-friendly CSS.
- The Agent may adapt layout and CSS to match the user’s brand or industry.
