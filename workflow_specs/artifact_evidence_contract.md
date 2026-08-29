# Artifact Evidence Contract

Use this contract for every generated analytical HTML artifact. It binds the
claims and visual output to actual query result files so labels cannot drift
from the data.

## Build sequence

1. Execute every evidence query through `scripts/sql_runner.py --out`.
2. Create a draft manifest JSON containing `queries`, `metrics`, `comparisons`,
   `charts`, and `findings`.
3. Run:

```bash
python scripts/artifact_manifest.py bind <output.html> <manifest-draft.json>
python scripts/validate_delivery.py <output.html>
```

The binder reads the evidence files and computes `result_sha256`, `row_count`,
`date_min`, and `date_max`; these values are not authored by the Agent.

## Minimal draft

```json
{
  "queries": [{
    "id": "q_period",
    "result_path": "query_results/period.json",
    "date_field": "period_date",
    "query_hash": "<query-hash>",
    "source_tables": ["fact_metric"]
  }],
  "metrics": [{"id": "primary_metric"}],
  "comparisons": [{
    "id": "cmp_primary",
    "type": "yoy",
    "calendar": "calendar",
    "current_start": "2026-01-01",
    "current_end": "2026-07-31",
    "baseline_start": "2025-01-01",
    "baseline_end": "2025-07-31",
    "current_period_status": "complete",
    "baseline_period_status": "complete",
    "alignment": "same_complete_periods",
    "metric_ids": ["primary_metric"],
    "evidence_query_ids": ["q_period"],
    "fingerprints": {
      "current": {
        "definition_hash": "metric-v1",
        "scope_hash": "entity-scope-v1",
        "filters_hash": "valid-records-v1",
        "unit": "count",
        "currency": "N/A",
        "timezone": "Asia/Shanghai"
      },
      "baseline": {
        "definition_hash": "metric-v1",
        "scope_hash": "entity-scope-v1",
        "filters_hash": "valid-records-v1",
        "unit": "count",
        "currency": "N/A",
        "timezone": "Asia/Shanghai"
      }
    }
  }],
  "findings": [{
    "id": "f1",
    "why_status": "tested",
    "evidence_query_ids": ["q_period"],
    "next_check": {"status": "executed", "query_id": "q_period"}
  }]
}
```

## Blocking rules

- Evidence files must still exist at validation time and match their bound
  SHA-256, row count, and date range.
- Period-comparison evidence must contain both declared windows and, by default,
  no dates outside those windows.
- The visible comparison contract and artifact manifest must declare identical
  windows.
- Current and baseline metric/scope fingerprints must match exactly.
- A finding marked `tested` must reference an executed next-check query.
- An artifact copied without its evidence files is not a fully auditable
  delivery pack; use `scripts/delivery_pack.py` when portability is required.
