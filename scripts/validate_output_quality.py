"""Enterprise quality gate for generated BI artifacts.

This validator is intentionally broader than ``validate_chart.py``. It applies
to query results, exports, Markdown reports, HTML reports, charts, dashboards,
and any other handoff artifact. The goal is to prevent "bare output": files
with numbers but no scope, no lineage, no evidence trail, or broken layout.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


GOVERNANCE_TOKENS = ("统计口径", "口径说明", "metric", "scope")
LINEAGE_TOKENS = ("数据血缘", "血缘", "lineage", "query hash", "query_hash", "数据来源", "来源表")
TIME_TOKENS = ("生成时间", "更新时间", "created_at", "generated_at")
LAYOUT_TOKENS = ("dashboard-grid", "chart-card", "report-page", "section", "table-scroll", "kpi-card")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _metadata_paths(path: Path) -> list[Path]:
    return [
        Path(str(path) + ".meta.json"),
        path.with_suffix(path.suffix + ".meta.json"),
        path.with_suffix(".meta.json"),
    ]


def _load_sidecar(path: Path) -> dict[str, Any] | None:
    for candidate in _metadata_paths(path):
        if not candidate.exists():
            continue
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"__invalid__": str(candidate)}
        if isinstance(data, dict):
            data["__path__"] = str(candidate)
            return data
    return None


def _has_any(text: str, tokens: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(token.lower() in lower for token in tokens)


def _validate_sidecar_artifact(path: Path, errors: list[str]) -> None:
    meta = _load_sidecar(path)
    if not meta:
        errors.append(
            "GOVERNANCE: query/export artifact has no metadata sidecar. "
            "Write `<artifact>.meta.json` with query_hash, source tables/columns, row_count, generated_at, and effective metrics."
        )
        return
    if "__invalid__" in meta:
        errors.append(f"GOVERNANCE: metadata sidecar is invalid JSON: {meta['__invalid__']}")
        return
    required = ("artifact_path", "artifact_type", "generated_at", "row_count", "columns", "query_hash", "effective_metrics")
    missing = [key for key in required if key not in meta or meta.get(key) in ("", None, [])]
    if missing:
        errors.append(f"GOVERNANCE: metadata sidecar `{meta.get('__path__')}` missing required fields: {missing}")
    if not meta.get("lineage_recorded"):
        errors.append("GOVERNANCE: metadata sidecar does not confirm lineage_recorded=true.")


def _validate_textual_artifact(path: Path, text: str, errors: list[str]) -> None:
    if len(text.strip()) < 240:
        errors.append("COMPLETENESS: artifact is too short for enterprise handoff; include summary, evidence, scope, and limitations.")
    if not _has_any(text, GOVERNANCE_TOKENS):
        errors.append("GOVERNANCE: missing visible statistical scope / 统计口径说明.")
    if not _has_any(text, LINEAGE_TOKENS):
        errors.append("GOVERNANCE: missing lineage / data source / query hash section.")
    if not _has_any(text, TIME_TOKENS):
        errors.append("GOVERNANCE: missing generated/updated timestamp.")
    number_count = len(re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?%?", text))
    if path.suffix.lower() in {".md", ".html", ".htm"} and number_count < 3:
        errors.append("EVIDENCE: too few numeric facts; enterprise analysis needs quantified evidence.")


def _validate_html_artifact(text: str, errors: list[str]) -> None:
    if "<style" not in text.lower():
        errors.append("LAYOUT: HTML artifact has no inline style block; avoid browser-default report/dashboard pages.")
    if not _has_any(text, LAYOUT_TOKENS):
        errors.append("LAYOUT: missing enterprise layout tokens such as report-page, dashboard-grid, chart-card, kpi-card, or table-scroll.")
    if re.search(r"<table\b", text, flags=re.IGNORECASE):
        row_count = len(re.findall(r"<tr\b", text, flags=re.IGNORECASE))
        if row_count > 18 and "table-scroll" not in text and "overflow" not in text:
            errors.append("LAYOUT: long HTML table lacks scroll/pagination wrapper.")


def validate_artifact(path: str | Path, artifact_type: str = "auto") -> list[str]:
    artifact = Path(path)
    errors: list[str] = []
    if not artifact.exists():
        return [f"MISSING: artifact not found: {artifact}"]

    suffix = artifact.suffix.lower()
    if artifact_type == "auto":
        if suffix in {".csv", ".json", ".xlsx", ".parquet"}:
            artifact_type = "query"
        elif suffix in {".html", ".htm"}:
            artifact_type = "html"
        else:
            artifact_type = "text"

    if artifact_type in {"query", "export"} or suffix in {".csv", ".json", ".xlsx", ".parquet"}:
        _validate_sidecar_artifact(artifact, errors)
        return errors

    text = _read_text(artifact)
    _validate_textual_artifact(artifact, text, errors)
    if artifact_type in {"html", "dashboard", "chart", "report"} or suffix in {".html", ".htm"}:
        _validate_html_artifact(text, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate enterprise quality of generated BI artifacts")
    parser.add_argument("artifact", help="Artifact path")
    parser.add_argument("--type", choices=["auto", "query", "export", "text", "html", "chart", "dashboard", "report"], default="auto")
    args = parser.parse_args(argv)

    errors = validate_artifact(args.artifact, args.type)
    if errors:
        print("INVALID enterprise BI artifact.", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("OK: artifact satisfies enterprise output quality gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
