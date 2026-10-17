# Data Cleaning Workflow

Use this workflow when handling `/clean`, `/清洗`, or any request to improve data
quality, standardize fields, remove duplicates, validate rules, or prepare data
for report/dashboard/modeling.

## Principle

Cleaning rules are business decisions. The Agent should guide the user to define
rules, infer safe defaults only when obvious, and clearly report every change.
Do not silently force cleaning assumptions.

Python scripts apply explicit rules. The Agent owns diagnosis, questioning,
rule design, and explanation.

## Project rules: discover once, reuse automatically

This section applies before **every analysis**, not only `/clean`. Business rules
are project-owned; the Skill only ships the engine and registry protocol.

- Work from the user project; invoke installed Skill scripts by absolute path.
  `ECHART_PROJECT_ROOT` or CLI `--project-root` selects an explicit project.
  Otherwise discovery stops at the nearest `.git`, `.echart-skill`, or
  `config/data_cleaning` ancestor. Never search sibling projects or global rules.
- `python <skill>/scripts/project_cleaning.py status` discovers
  `<project>/config/data_cleaning/manifest.json`. No registry means no automatic
  cleaning. Orphan JSON files without a manifest, malformed rules, conflicting
  bindings, and paths/symlinks outside the project are errors, not defaults.
- When the user says “remember this cleaning rule” or adds a rule, inspect the
  existing registry and update that dataset's declarative JSON. Do not require
  the user to supply a technical manifest or repeat a long prompt. Clarify only
  choices that materially change business meaning. Unknown rule types require
  implementation/tests before registration; do not load arbitrary project code.
- Run `project_cleaning.py preview <dataset>` to check impact without changing
  source data or approval. After the user authorizes the rule and its impact,
  run `project_cleaning.py approve <dataset>`. Explicitly specified rules may be
  approved within that authorized scope; inferred destructive rules need consent.
  Approval binds rules, source binding, check thresholds and engine code by hash.
  Changed rules/engine require a new preview and approval, never auto-approval.
- Ordinary `sql_runner.py --db ... --sql ...` and `analysis_runner.py` local
  queries now load approved rules automatically. No cleaning CLI flags required.
  All registered datasets in that database are validated in one raw transaction
  snapshot, then exposed as isolated temporary relations under the same names.
  CTEs, joins and `main.<table>` work; catalog-qualified raw bypasses are blocked.
  Do not rewrite aggregate output after querying; cleaning precedes aggregation.
- Every query recomputes from raw data; there is no stale cleaned-table cache or
  cumulative transformation. Source tables are never overwritten. New nulls,
  rule violations, unknown fields/options and failed thresholds block execution;
  never fall back to raw data or reuse a previous successful output as new.
- Successful result `.meta.json` includes `project_cleaning`, with rule hash,
  source snapshot hash, counts and checks. A bounded latest summary lives in
  `.echart-skill/cleaning/latest.json`; it is not an execution cache or proof of
  the next run. No raw samples or replacement-map contents are copied to it.

### Minimal project configuration

The following is a schema example, not a default business rule to install.
Paths are relative to the project root; table names address the local `main`
schema. One binding per database/table; one rule file can combine operations.

`config/data_cleaning/manifest.json`:

```json
{
  "version": 1,
  "datasets": [{
    "id": "orders",
    "db": "data/workspace.duckdb",
    "table": "orders_raw",
    "rules": "config/data_cleaning/orders.json",
    "checks": {"max_new_nulls": 0, "max_rule_violations": 0, "min_output_rows": 1}
  }]
}
```

`config/data_cleaning/orders.json`:

```json
{
  "text_cleaning": [{"column": "region", "strip": true}],
  "type_conversions": [{"column": "amount", "type": "money", "decimals": 2}]
}
```

`approve` writes `approved_sha256`; never fabricate that value. Optional checks:
`max_removed_rows` (default no extra cap), `max_new_nulls` (default 0),
`max_rule_violations` (default 0), `min_output_rows` (default 1). An intentional
nullification/drop must be consistent with the approved thresholds. A legitimate
empty dataset can explicitly use `min_output_rows: 0`.

No implicit deduplication: set `deduplicate: true` for full-row deduplication or
specify `unique_key` for keyed deduplication. `latest` requires an ascending,
correctly typed `duplicate_order_by`. No grouping/aggregation dedupe is implied.
Do not put legacy `output_table` or `report_path` keys in registry rule JSON;
automatic execution owns temporary results and receipts.

### External sources and execution boundary

Automatic execution currently supports project-local DuckDB main-schema tables,
including imported file/database snapshots. Refresh via `data_importer.py` or
`db_cli.py import` before analyzing updated external data; verify the source's
coverage and freshness, not just the cleaning hash. Optional binding metadata
`"origin": {"profile": "sales", "table": "public.orders"}` records a named remote
source. Its audited direct-query path blocks analysis and directs the Agent to
the governed local snapshot; import/schema inspection remain available.

The hook is in `sql_runner`/`analysis_runner`, not every DuckDB client. Do not use
direct repository calls, a different connection identity, raw files, unregistered
copies, or alternative tools to evade it. Direct DSN/host identity equivalence is
not inferred; resolve and register the named profile first. Large tables are
currently processed in pandas memory; do not claim streaming cleaning. Arbitrary
project SQL/Python plugins, non-main schemas and cross-database automatic cleaning
are not supported by this registry version. Unsupported scope must be stated,
not silently treated as clean. Cross-table rule checks use raw tables in the same
snapshot (not another dataset's already-cleaned result).

## Required Steps

1. **Profile the data first**
   - Inspect table names, column names, types, sample values, row count, missing rate, duplicate candidates, date-like columns, money-like columns, ID-like columns.
   - Identify likely grain: order, user, event, product, transaction, daily aggregate, etc.
   - Identify candidate unique keys, including multi-column keys.

2. **Ask cleaning questions when rules are ambiguous**
   - What is the unique key? Can it be multiple columns?
   - For duplicate keys, keep latest, first, last, aggregate, or flag?
   - Which columns are dates, money, numeric, boolean, category, text, or PII?
   - How should missing values be handled by column?
   - What business ranges define invalid values?
   - Which fields must be logically consistent?
   - Are there cross-table rules, such as registration date <= first purchase date?

3. **Build a cleaning plan**
   - List proposed rules before applying them.
   - Mark rules as user-specified, inferred-safe, or needs confirmation.
   - Do not apply destructive changes without user confirmation unless explicitly requested.
   - Prefer writing to a new output table, e.g. `<table>_cleaned`.

4. **Apply configurable cleaning**
   - Use `scripts/data_cleaner.py table <table> --config <rules.json>`.
   - Use Python only to execute explicit rules and produce a cleaning report.
   - Preserve source table unless the user explicitly asks to overwrite.

5. **Validate after cleaning**
   - Compare before/after row counts, missing rates, duplicate counts, data types, rule violations, and outlier counts.
   - Report dropped/nullified/flagged rows.
   - If cleaning introduced new nulls through type conversion, surface them.

## Supported Cleaning Rule Types

- **Type and format conversion**: DATE, datetime, money with 2 decimals, numeric, integer, boolean, text.
- **Missing values**: drop, mean, median, mode, constant, or preserve.
- **Duplicate handling**: explicit full-row deduplication (`deduplicate: true`), multi-column unique keys, keep first/last/latest; otherwise preserve duplicates.
- **Outlier handling**: business bounds, IQR, Z-score; flag, null, clip, or drop.
- **Normalization and standardization**: min-max and z-score.
- **Consistency and text cleaning**: strip, case normalization, special-character removal, controlled replacement.
- **Rule engine**: field logic checks such as `start_date <= end_date` or `paid_amount <= order_amount`.
- **Cross-table validation**: join by one or more keys and validate business logic.
- **Feature engineering and masking**: date parts, weekend flags, ratios, concatenated keys, phone/customer masking.

## Rule Config Example

```json
{
  "output_table": "orders_cleaned",
  "unique_key": ["order_id", "line_id"],
  "duplicate_keep": "latest",
  "duplicate_order_by": "updated_at",
  "type_conversions": [
    {"column": "order_date", "type": "date"},
    {"column": "paid_amount", "type": "money", "decimals": 2},
    {"column": "is_member", "type": "boolean", "true_values": ["是", "Y"], "false_values": ["否", "N"]}
  ],
  "missing_values": {
    "customer_level": {"strategy": "constant", "value": "unknown"},
    "age": {"strategy": "median"}
  },
  "outliers": [
    {"column": "age", "method": "bounds", "min": 0, "max": 150, "action": "null"},
    {"column": "paid_amount", "method": "iqr", "action": "flag"}
  ],
  "text_cleaning": [
    {"column": "province", "strip": true, "replace": {"省": ""}}
  ],
  "rules": [
    {"name": "register_before_purchase", "left": "register_date", "op": "<=", "right": "first_purchase_date", "action": "flag"}
  ],
  "cross_table_rules": [
    {
      "name": "user_register_before_first_purchase",
      "table": "first_purchases",
      "key": ["user_id"],
      "left": "register_date",
      "op": "<=",
      "right": "first_purchase_date"
    }
  ],
  "derived_features": [
    {"name": "order_month", "method": "date_part", "source": "order_date", "part": "month"},
    {"name": "amount_per_item", "method": "ratio", "numerator": "paid_amount", "denominator": "quantity", "decimals": 2}
  ],
  "masking": [
    {"column": "phone", "method": "middle", "keep_start": 3, "keep_end": 4}
  ],
  "report_path": "outputs/reports/orders_cleaning_report.json"
}
```

## Agent Question Checklist

Ask only questions that materially affect the cleaning result:

- “这张表的一行代表什么？订单、用户、事件还是汇总行？”
- “唯一键是哪几个字段？重复时保留最新还是按业务聚合？”
- “这些日期字段是否只保留日期，不保留时分秒？”
- “金额字段是否统一为两位小数？负数是否允许？”
- “缺失值是删除、填补、保留，还是单独标记？”
- “哪些异常是业务异常需要保留，哪些是脏数据需要修正？”
- “是否需要跨表校验？例如用户注册日期早于首次购买日期。”

## Output Requirements

The Agent should return:

- Cleaning plan.
- Cleaned table name.
- Before/after quality summary.
- Rule execution report.
- Remaining risks and unresolved questions.
- Suggested next analysis step.
