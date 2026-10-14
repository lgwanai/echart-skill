#!/usr/bin/env python3
"""Bind query evidence to an HTML artifact and validate the embedded manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any


MANIFEST_ID = "analysis-artifact-manifest"
COMPARISON_CONTRACT_ID = "analysis-comparison-contract"
COMPARISON_BINDING_FIELDS = (
    "type",
    "calendar",
    "current_start",
    "current_end",
    "baseline_start",
    "baseline_end",
    "current_period_status",
    "baseline_period_status",
    "alignment",
)
FINGERPRINT_FIELDS = (
    "definition_hash",
    "scope_hash",
    "filters_hash",
    "unit",
    "currency",
    "timezone",
)


def _load_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        if isinstance(payload, dict):
            for key in ("rows", "data", "results"):
                if isinstance(payload.get(key), list):
                    return [row for row in payload[key] if isinstance(row, dict)]
    raise ValueError(f"query evidence must be CSV or row-oriented JSON: {path}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _date_values(rows: list[dict[str, Any]], field: str, prefix: str) -> list[date]:
    values: list[date] = []
    for index, row in enumerate(rows):
        value = row.get(field)
        if value in (None, ""):
            continue
        try:
            values.append(date.fromisoformat(str(value)[:10]))
        except ValueError as exc:
            raise ValueError(f"{prefix} row {index} has non-ISO date in {field}: {value!r}") from exc
    if not values:
        raise ValueError(f"{prefix} has no usable dates in field {field!r}")
    return values


def _sidecar(path: Path) -> dict[str, Any] | None:
    candidates = [Path(str(path) + ".meta.json"), path.with_suffix(".meta.json")]
    for candidate in candidates:
        if candidate.is_file():
            payload = json.loads(candidate.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else None
    return None


def materialize_manifest(draft: dict[str, Any], draft_path: Path, html_path: Path) -> dict[str, Any]:
    manifest = json.loads(json.dumps(draft))
    manifest["version"] = 1
    queries = manifest.get("queries")
    if not isinstance(queries, list) or not queries:
        raise ValueError("manifest.queries must contain at least one query evidence entry")
    for index, query in enumerate(queries):
        if not isinstance(query, dict):
            raise ValueError(f"manifest.queries[{index}] must be an object")
        result_path = query.pop("result_path", None)
        if not isinstance(result_path, str) or not result_path.strip():
            raise ValueError(f"manifest.queries[{index}].result_path is required")
        resolved = (draft_path.parent / result_path).resolve()
        if not resolved.is_file():
            raise ValueError(f"query evidence not found: {resolved}")
        rows = _load_rows(resolved)
        date_field = query.get("date_field")
        dates = _date_values(rows, date_field, f"manifest.queries[{index}]") if date_field else []
        sidecar = _sidecar(resolved)
        sidecar_hash = sidecar.get("query_hash") if sidecar else None
        declared_hash = query.get("query_hash")
        if sidecar_hash and declared_hash and sidecar_hash != declared_hash:
            raise ValueError(f"manifest.queries[{index}].query_hash does not match metadata sidecar")
        query["query_hash"] = declared_hash or sidecar_hash
        if not isinstance(query["query_hash"], str) or not query["query_hash"].strip():
            raise ValueError(f"manifest.queries[{index}].query_hash is required")
        query["result_ref"] = os.path.relpath(resolved, html_path.parent.resolve())
        query["result_sha256"] = _sha256(resolved)
        query["row_count"] = len(rows)
        if dates:
            query["date_min"] = min(dates).isoformat()
            query["date_max"] = max(dates).isoformat()
    return manifest


def _extract_json_script(content: str, script_id: str) -> tuple[dict[str, Any] | None, list[str]]:
    pattern = re.compile(
        rf'<script\b(?=[^>]*\bid=["\']{re.escape(script_id)}["\'])(?=[^>]*\btype=["\']application/json["\'])[^>]*>(.*?)</script\s*>',
        re.IGNORECASE | re.DOTALL,
    )
    matches = pattern.findall(content)
    if not matches:
        return None, [f"missing application/json #{script_id}"]
    if len(matches) > 1:
        return None, [f"duplicate application/json #{script_id}"]
    try:
        payload = json.loads(matches[0])
    except json.JSONDecodeError as exc:
        return None, [f"#{script_id} contains invalid JSON: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"#{script_id} root must be an object"]
    return payload, []


def embed_manifest(html_path: Path, manifest: dict[str, Any]) -> None:
    content = html_path.read_text(encoding="utf-8")
    tag = (
        f'<script type="application/json" id="{MANIFEST_ID}">'
        + json.dumps(manifest, ensure_ascii=False, allow_nan=False, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        + "</script>"
    )
    pattern = re.compile(
        rf'<script\b(?=[^>]*\bid=["\']{MANIFEST_ID}["\'])[^>]*>.*?</script\s*>',
        re.IGNORECASE | re.DOTALL,
    )
    if pattern.search(content):
        content = pattern.sub(lambda _: tag, content, count=1)
    elif "</head>" in content.lower():
        content = re.sub(r"</head>", lambda _: tag + "\n</head>", content, count=1, flags=re.IGNORECASE)
    else:
        raise ValueError("HTML has no </head> for manifest insertion")
    html_path.write_text(content, encoding="utf-8")


def _parse_date(value: Any, field: str, errors: list[str]) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        errors.append(f"{field} must be an ISO date")
        return None


def validate_manifest(manifest: dict[str, Any], html_path: Path) -> list[str]:
    errors: list[str] = []
    if manifest.get("version") != 1:
        errors.append("manifest.version must be 1")
    query_map: dict[str, tuple[dict[str, Any], list[date]]] = {}
    for index, query in enumerate(manifest.get("queries", [])):
        prefix = f"manifest.queries[{index}]"
        if not isinstance(query, dict):
            errors.append(f"{prefix} must be an object")
            continue
        query_id = query.get("id")
        if not isinstance(query_id, str) or not query_id:
            errors.append(f"{prefix}.id is required")
            continue
        result_ref = query.get("result_ref")
        if not isinstance(result_ref, str) or not result_ref:
            errors.append(f"{prefix}.result_ref is required")
            continue
        result_path = (html_path.parent / result_ref).resolve()
        if not result_path.is_file():
            errors.append(f"{prefix} evidence file not found: {result_ref}")
            continue
        if _sha256(result_path) != query.get("result_sha256"):
            errors.append(f"{prefix}.result_sha256 does not match evidence file")
        try:
            rows = _load_rows(result_path)
            dates = _date_values(rows, str(query["date_field"]), prefix) if query.get("date_field") else []
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
            continue
        if len(rows) != query.get("row_count"):
            errors.append(f"{prefix}.row_count does not match evidence file")
        if dates and (min(dates).isoformat() != query.get("date_min") or max(dates).isoformat() != query.get("date_max")):
            errors.append(f"{prefix} date_min/date_max do not match evidence file")
        if not isinstance(query.get("query_hash"), str) or not query["query_hash"]:
            errors.append(f"{prefix}.query_hash is required")
        query_map[query_id] = (query, dates)

    metric_ids = {
        metric.get("id") for metric in manifest.get("metrics", [])
        if isinstance(metric, dict) and isinstance(metric.get("id"), str)
    }
    for index, comparison in enumerate(manifest.get("comparisons", [])):
        prefix = f"manifest.comparisons[{index}]"
        if not isinstance(comparison, dict):
            errors.append(f"{prefix} must be an object")
            continue
        evidence_ids = comparison.get("evidence_query_ids")
        if not isinstance(evidence_ids, list) or not evidence_ids:
            errors.append(f"{prefix}.evidence_query_ids requires at least one query")
            continue
        linked = [query_map[query_id] for query_id in evidence_ids if query_id in query_map]
        if len(linked) != len(evidence_ids):
            errors.append(f"{prefix}.evidence_query_ids references unknown query")
            continue
        linked_metric_ids = comparison.get("metric_ids")
        if not isinstance(linked_metric_ids, list) or not linked_metric_ids:
            errors.append(f"{prefix}.metric_ids requires at least one metric")
        elif any(metric_id not in metric_ids for metric_id in linked_metric_ids):
            errors.append(f"{prefix}.metric_ids references unknown metric")
        current_start = _parse_date(comparison.get("current_start"), f"{prefix}.current_start", errors)
        current_end = _parse_date(comparison.get("current_end"), f"{prefix}.current_end", errors)
        baseline_start = _parse_date(comparison.get("baseline_start"), f"{prefix}.baseline_start", errors)
        baseline_end = _parse_date(comparison.get("baseline_end"), f"{prefix}.baseline_end", errors)
        if all((current_start, current_end, baseline_start, baseline_end)):
            for query, dates in linked:
                current_dates = [value for value in dates if current_start <= value <= current_end]
                baseline_dates = [value for value in dates if baseline_start <= value <= baseline_end]
                if not current_dates or not baseline_dates:
                    errors.append(f"{prefix}: query {query['id']} does not contain both comparison windows")
                if not query.get("allow_extra_periods", False):
                    outside = [
                        value for value in dates
                        if not (current_start <= value <= current_end or baseline_start <= value <= baseline_end)
                    ]
                    if outside:
                        errors.append(
                            f"{prefix}: query {query['id']} contains dates outside declared comparison windows"
                        )
        fingerprints = comparison.get("fingerprints")
        if not isinstance(fingerprints, dict):
            errors.append(f"{prefix}.fingerprints must contain current and baseline")
        else:
            current_fp = fingerprints.get("current")
            baseline_fp = fingerprints.get("baseline")
            for side, fingerprint in (("current", current_fp), ("baseline", baseline_fp)):
                if not isinstance(fingerprint, dict):
                    errors.append(f"{prefix}.fingerprints.{side} must be an object")
                    continue
                missing = [field for field in FINGERPRINT_FIELDS if not isinstance(fingerprint.get(field), str)]
                if missing:
                    errors.append(f"{prefix}.fingerprints.{side} missing {missing}")
            if isinstance(current_fp, dict) and isinstance(baseline_fp, dict) and current_fp != baseline_fp:
                errors.append(f"{prefix}: current and baseline metric/scope fingerprints differ")

    for index, finding in enumerate(manifest.get("findings", [])):
        prefix = f"manifest.findings[{index}]"
        if not isinstance(finding, dict):
            errors.append(f"{prefix} must be an object")
            continue
        evidence_ids = finding.get("evidence_query_ids")
        if not isinstance(evidence_ids, list) or not evidence_ids:
            errors.append(f"{prefix}.evidence_query_ids requires evidence")
        elif any(query_id not in query_map for query_id in evidence_ids):
            errors.append(f"{prefix}.evidence_query_ids references unknown query")
        if finding.get("why_status") == "tested":
            next_check = finding.get("next_check")
            if not isinstance(next_check, dict) or next_check.get("status") != "executed":
                errors.append(f"{prefix}: tested findings require an executed next_check")
            elif next_check.get("query_id") not in query_map:
                errors.append(f"{prefix}.next_check.query_id references unknown query")
    return errors


def validate_embedded_manifest(content: str, html_path: Path) -> list[str]:
    manifest, errors = _extract_json_script(content, MANIFEST_ID)
    if errors:
        return errors
    return validate_manifest(manifest or {}, html_path)


def validate_comparison_binding(content: str) -> list[str]:
    contract, contract_errors = _extract_json_script(content, COMPARISON_CONTRACT_ID)
    manifest, manifest_errors = _extract_json_script(content, MANIFEST_ID)
    if contract_errors or manifest_errors:
        return contract_errors + manifest_errors
    contract_comparisons = contract.get("comparisons", []) if contract else []
    manifest_comparisons = manifest.get("comparisons", []) if manifest else []
    errors: list[str] = []
    for index, comparison in enumerate(contract_comparisons):
        if not isinstance(comparison, dict):
            continue
        matches = [
            candidate for candidate in manifest_comparisons
            if isinstance(candidate, dict)
            and all(
                candidate.get(field, "calendar" if field == "calendar" else None)
                == comparison.get(field, "calendar" if field == "calendar" else None)
                for field in COMPARISON_BINDING_FIELDS
            )
        ]
        if not matches:
            errors.append(
                f"comparison contract entry {index} is not identically bound in #{MANIFEST_ID}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    bind = subparsers.add_parser("bind")
    bind.add_argument("html", type=Path)
    bind.add_argument("draft", type=Path)
    validate = subparsers.add_parser("validate")
    validate.add_argument("html", type=Path)
    args = parser.parse_args()
    if args.command == "bind":
        draft = json.loads(args.draft.read_text(encoding="utf-8"))
        manifest = materialize_manifest(draft, args.draft, args.html)
        errors = validate_manifest(manifest, args.html)
        if errors:
            for error in errors:
                print(f"- {error}")
            return 1
        embed_manifest(args.html, manifest)
        print(f"PASS: bound query evidence into {args.html}")
        return 0
    content = args.html.read_text(encoding="utf-8")
    errors = validate_embedded_manifest(content, args.html)
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: artifact manifest matches query evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
