import json
from pathlib import Path

from scripts.artifact_manifest import (
    embed_manifest,
    materialize_manifest,
    validate_embedded_manifest,
    validate_comparison_binding,
    validate_manifest,
)


FINGERPRINT = {
    "definition_hash": "metric-v1",
    "scope_hash": "all-entities-v1",
    "filters_hash": "valid-records-v1",
    "unit": "CNY",
    "currency": "CNY",
    "timezone": "Asia/Shanghai",
}


def _draft(result_path: str):
    return {
        "queries": [{
            "id": "q_period",
            "result_path": result_path,
            "date_field": "period_date",
            "query_hash": "sql-hash-1",
            "source_tables": ["fact_metric"],
        }],
        "metrics": [{"id": "revenue"}],
        "comparisons": [{
            "id": "cmp_revenue_yoy",
            "type": "yoy",
            "current_start": "2026-01-01",
            "current_end": "2026-07-31",
            "baseline_start": "2025-01-01",
            "baseline_end": "2025-07-31",
            "metric_ids": ["revenue"],
            "evidence_query_ids": ["q_period"],
            "fingerprints": {
                "current": dict(FINGERPRINT),
                "baseline": dict(FINGERPRINT),
            },
        }],
        "findings": [{
            "id": "f1",
            "why_status": "tested",
            "evidence_query_ids": ["q_period"],
            "next_check": {"status": "executed", "query_id": "q_period"},
        }],
    }


def _write_rows(path: Path, extra_date: str | None = None):
    rows = [
        {"period_date": "2025-01-01", "value": 100},
        {"period_date": "2025-07-31", "value": 120},
        {"period_date": "2026-01-01", "value": 130},
        {"period_date": "2026-07-31", "value": 140},
    ]
    if extra_date:
        rows.append({"period_date": extra_date, "value": 999})
    path.write_text(json.dumps(rows), encoding="utf-8")


def test_manifest_binds_query_file_and_validates_embedded_evidence(tmp_path: Path):
    result = tmp_path / "period.json"
    html = tmp_path / "dashboard.html"
    draft_path = tmp_path / "manifest-draft.json"
    _write_rows(result)
    html.write_text("<html><head></head><body></body></html>", encoding="utf-8")
    draft_path.write_text(json.dumps(_draft(result.name)), encoding="utf-8")

    manifest = materialize_manifest(_draft(result.name), draft_path, html)
    embed_manifest(html, manifest)

    assert validate_embedded_manifest(html.read_text(encoding="utf-8"), html) == []


def test_manifest_rejects_dates_outside_declared_windows(tmp_path: Path):
    result = tmp_path / "period.json"
    html = tmp_path / "dashboard.html"
    draft_path = tmp_path / "manifest-draft.json"
    _write_rows(result, extra_date="2025-12-31")
    html.write_text("<html><head></head><body></body></html>", encoding="utf-8")

    manifest = materialize_manifest(_draft(result.name), draft_path, html)
    errors = validate_manifest(manifest, html)

    assert any("outside declared comparison windows" in error for error in errors)


def test_manifest_rejects_evidence_changed_after_binding(tmp_path: Path):
    result = tmp_path / "period.json"
    html = tmp_path / "dashboard.html"
    draft_path = tmp_path / "manifest-draft.json"
    _write_rows(result)
    html.write_text("<html><head></head><body></body></html>", encoding="utf-8")
    manifest = materialize_manifest(_draft(result.name), draft_path, html)
    _write_rows(result, extra_date="2026-07-15")

    errors = validate_manifest(manifest, html)

    assert any("result_sha256" in error for error in errors)


def test_manifest_rejects_metric_scope_fingerprint_drift(tmp_path: Path):
    result = tmp_path / "period.json"
    html = tmp_path / "dashboard.html"
    draft_path = tmp_path / "manifest-draft.json"
    _write_rows(result)
    html.write_text("<html><head></head><body></body></html>", encoding="utf-8")
    draft = _draft(result.name)
    draft["comparisons"][0]["fingerprints"]["baseline"]["scope_hash"] = "different-scope"
    manifest = materialize_manifest(draft, draft_path, html)

    errors = validate_manifest(manifest, html)

    assert any("fingerprints differ" in error for error in errors)


def test_tested_finding_requires_executed_query(tmp_path: Path):
    result = tmp_path / "period.json"
    html = tmp_path / "dashboard.html"
    draft_path = tmp_path / "manifest-draft.json"
    _write_rows(result)
    html.write_text("<html><head></head><body></body></html>", encoding="utf-8")
    draft = _draft(result.name)
    draft["findings"][0]["next_check"] = {"status": "planned", "query_id": "q_period"}
    manifest = materialize_manifest(draft, draft_path, html)

    errors = validate_manifest(manifest, html)

    assert any("require an executed next_check" in error for error in errors)


def test_visible_comparison_contract_must_match_bound_manifest(tmp_path: Path):
    result = tmp_path / "period.json"
    html = tmp_path / "dashboard.html"
    draft_path = tmp_path / "manifest-draft.json"
    _write_rows(result)
    html.write_text("<html><head></head><body></body></html>", encoding="utf-8")
    manifest = materialize_manifest(_draft(result.name), draft_path, html)
    embed_manifest(html, manifest)
    comparison = dict(manifest["comparisons"][0])
    comparison.update({
        "calendar": "calendar",
        "current_period_status": "complete",
        "baseline_period_status": "complete",
        "alignment": "same_complete_periods",
    })
    manifest["comparisons"][0].update({
        "calendar": "calendar",
        "current_period_status": "complete",
        "baseline_period_status": "complete",
        "alignment": "same_complete_periods",
    })
    embed_manifest(html, manifest)
    contract_tag = (
        '<script type="application/json" id="analysis-comparison-contract">'
        + json.dumps({"version": 1, "comparisons": [comparison]})
        + "</script>"
    )
    content = html.read_text(encoding="utf-8").replace("</head>", contract_tag + "</head>")

    assert validate_comparison_binding(content) == []
    changed = content.replace('"current_end": "2026-07-31"', '"current_end": "2026-12-31"', 1)
    assert any("not identically bound" in error for error in validate_comparison_binding(changed))
