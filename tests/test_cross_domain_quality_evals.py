import json
from pathlib import Path

import pytest

from scripts.artifact_manifest import materialize_manifest, validate_manifest
from scripts.chart_capabilities import recommend_view
from scripts.validate_analysis_plan import validate_comparison


ROOT = Path(__file__).resolve().parents[1]
CASES = [
    pytest.param(path, id=path.stem)
    for path in sorted((ROOT / "tests/fixtures/domain_evals").glob("*.json"))
]
BASE_FINGERPRINT = {
    "definition_hash": "metric-v1",
    "scope_hash": "governed-scope-v1",
    "filters_hash": "valid-records-v1",
    "unit": "count",
    "currency": "N/A",
    "timezone": "Asia/Shanghai",
}


@pytest.mark.parametrize("case_path", CASES)
def test_cross_domain_quality_case(case_path: Path, tmp_path: Path):
    case = json.loads(case_path.read_text(encoding="utf-8"))
    result_path = tmp_path / f"{case['domain']}.json"
    result_path.write_text(json.dumps(case["rows"]), encoding="utf-8")
    html_path = tmp_path / f"{case['domain']}.html"
    html_path.write_text("<html><head></head><body></body></html>", encoding="utf-8")
    current_fp = dict(BASE_FINGERPRINT)
    baseline_fp = dict(BASE_FINGERPRINT)
    if case.get("baseline_scope_hash"):
        baseline_fp["scope_hash"] = case["baseline_scope_hash"]
    comparison = dict(case["comparison"])
    manifest_comparison = dict(comparison)
    manifest_comparison.update({
        "metric_ids": ["metric"],
        "evidence_query_ids": ["q1"],
        "fingerprints": {"current": current_fp, "baseline": baseline_fp},
    })
    draft = {
        "queries": [{
            "id": "q1",
            "result_path": result_path.name,
            "date_field": "period_date",
            "query_hash": f"{case['domain']}-query-v1",
        }],
        "metrics": [{"id": "metric"}],
        "comparisons": [manifest_comparison],
        "findings": [{
            "id": "f1",
            "why_status": "tested",
            "evidence_query_ids": ["q1"],
            "next_check": {"status": "executed", "query_id": "q1"},
        }],
    }
    draft_path = tmp_path / "draft.json"
    manifest = materialize_manifest(draft, draft_path, html_path)
    errors = validate_comparison(comparison) + validate_manifest(manifest, html_path)
    recommendation = recommend_view(case["view_request"])

    assert recommendation["selected"]["view"] == case["expected_view"]
    if case["expected_error"]:
        assert any(case["expected_error"] in error for error in errors), errors
    else:
        assert errors == []
