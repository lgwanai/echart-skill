#!/usr/bin/env python3
"""Validate chart/report/dashboard expression plans before rendering."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

try:
    from scripts.chart_capabilities import allowed_views
except ModuleNotFoundError:
    from chart_capabilities import allowed_views


ALLOWED_MODES = {"exploration", "decision_support", "monitoring"}
TABLE_MODES = {"source_toggle", "companion", "primary"}
WHY_STATUSES = {"tested", "hypothesis", "unknown"}
COMPARISON_TYPES = {"yoy", "qoq", "mom", "wow", "period", "cohort"}
PERIOD_STATUSES = {"complete", "partial"}
CALENDAR_TYPES = {"calendar", "fiscal", "retail_445", "custom"}
ALIGNMENTS = {
    "same_complete_periods",
    "same_elapsed_days",
    "same_named_periods",
    "same_cohort_age",
}
RELATIONS = {
    "single_value", "deviation", "correlation", "ranking", "distribution",
    "time", "magnitude", "composition", "spatial", "flow",
}
SIGNAL_WORDS = {
    "高于", "低于", "领先", "落后", "增长", "下降", "集中", "占", "缺口", "异常",
    "相关", "波动", "流失", "改善", "恶化", "超过", "不足", "持平", "反超", "峰值",
    "低谷", "贡献", "拖累", "偏高", "偏低", "增加", "减少", "上升", "下滑",
    "higher", "lower", "lead", "lag", "increase", "decrease", "decline", "grow",
    "concentrat", "share", "gap", "anomal", "correlat", "improve", "worsen",
    "exceed", "peak", "trough", "contribut", "drag", "flat", "volatile",
}
COMPARISON_HINTS = {
    "同比", "环比", "同期", "对比", "较上", "较去",
    "yoy", "qoq", "mom", "wow", " vs ", "versus",
}


def _filled(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_date(value: Any, field: str, errors: list[str]) -> date | None:
    if not _filled(value):
        errors.append(f"{field}: required ISO date")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{field}: must use YYYY-MM-DD")
        return None


def _validate_comparison(comparison: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(comparison, dict):
        errors.append(f"{prefix}.comparison: required for period comparison claims")
        return

    comparison_type = comparison.get("type")
    if comparison_type not in COMPARISON_TYPES:
        errors.append(f"{prefix}.comparison.type: must be one of {sorted(COMPARISON_TYPES)}")
    current_status = comparison.get("current_period_status")
    baseline_status = comparison.get("baseline_period_status")
    if current_status not in PERIOD_STATUSES:
        errors.append(f"{prefix}.comparison.current_period_status: must be complete or partial")
    if baseline_status not in PERIOD_STATUSES:
        errors.append(f"{prefix}.comparison.baseline_period_status: must be complete or partial")
    if current_status in PERIOD_STATUSES and baseline_status in PERIOD_STATUSES and current_status != baseline_status:
        errors.append(f"{prefix}.comparison: partial and complete periods cannot be compared")
    alignment = comparison.get("alignment")
    if alignment not in ALIGNMENTS:
        errors.append(f"{prefix}.comparison.alignment: must be one of {sorted(ALIGNMENTS)}")
    if current_status == "partial" and alignment != "same_elapsed_days":
        errors.append(f"{prefix}.comparison.alignment: partial periods require same_elapsed_days")
    if comparison.get("comparable") is not True:
        errors.append(f"{prefix}.comparison.comparable: must be true after alignment checks")

    calendar_type = comparison.get("calendar", "calendar")
    if calendar_type not in CALENDAR_TYPES:
        errors.append(f"{prefix}.comparison.calendar: must be one of {sorted(CALENDAR_TYPES)}")
    if calendar_type != "calendar" and alignment == "same_complete_periods":
        errors.append(
            f"{prefix}.comparison.alignment: fiscal/retail/custom calendars require "
            "same_named_periods or same_elapsed_days"
        )
    if alignment == "same_named_periods":
        for key in ("current_period_key", "baseline_period_key"):
            if not _filled(comparison.get(key)):
                errors.append(f"{prefix}.comparison.{key}: required for same_named_periods")

    current_start = _parse_date(comparison.get("current_start"), f"{prefix}.comparison.current_start", errors)
    current_end = _parse_date(comparison.get("current_end"), f"{prefix}.comparison.current_end", errors)
    baseline_start = _parse_date(comparison.get("baseline_start"), f"{prefix}.comparison.baseline_start", errors)
    baseline_end = _parse_date(comparison.get("baseline_end"), f"{prefix}.comparison.baseline_end", errors)
    latest_complete = _parse_date(
        comparison.get("latest_complete_period_end"),
        f"{prefix}.comparison.latest_complete_period_end",
        errors,
    )
    if current_start and current_end and current_start > current_end:
        errors.append(f"{prefix}.comparison: current_start must not follow current_end")
    if baseline_start and baseline_end and baseline_start > baseline_end:
        errors.append(f"{prefix}.comparison: baseline_start must not follow baseline_end")
    if current_status == "complete" and current_end and latest_complete and current_end > latest_complete:
        errors.append(f"{prefix}.comparison: current_end exceeds the latest complete period")
    if (
        comparison_type == "yoy"
        and calendar_type == "calendar"
        and all((current_start, current_end, baseline_start, baseline_end))
    ):
        if current_start.year != baseline_start.year + 1 or current_end.year != baseline_end.year + 1:
            errors.append(f"{prefix}.comparison: YoY windows must be exactly one year apart")
        if (current_start.month, current_start.day) != (baseline_start.month, baseline_start.day):
            errors.append(f"{prefix}.comparison: YoY start month/day must align")
        if (current_end.month, current_end.day) != (baseline_end.month, baseline_end.day):
            errors.append(f"{prefix}.comparison: YoY end month/day must align")


def validate_comparison(comparison: Any, prefix: str = "comparison") -> list[str]:
    """Validate one reusable period-comparison contract.

    The same rules are used by the pre-render analysis-plan gate and by the
    final standalone-HTML gate. Keeping one implementation prevents a report
    from passing planning with one definition and shipping with another.
    """
    errors: list[str] = []
    _validate_comparison(comparison, prefix, errors)
    return errors


def validate_plan(plan: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["root: plan must be a JSON object"]

    for key in ("decision_context", "audience"):
        if not _filled(plan.get(key)):
            errors.append(f"{key}: required non-empty string")

    mode = plan.get("analysis_mode")
    if mode not in ALLOWED_MODES:
        errors.append(f"analysis_mode: must be one of {sorted(ALLOWED_MODES)}")

    questions = plan.get("questions")
    if not isinstance(questions, list) or not questions or not all(_filled(q) for q in questions):
        errors.append("questions: require at least one non-empty question")

    views = plan.get("views")
    if not isinstance(views, list) or not views:
        errors.append("views: require at least one planned view")
        views = []

    for index, view in enumerate(views):
        prefix = f"views[{index}]"
        if not isinstance(view, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        for key in ("id", "message", "relation", "primary_view", "reason", "evidence_ref"):
            if not _filled(view.get(key)):
                errors.append(f"{prefix}.{key}: required non-empty string")

        message = view.get("message", "")
        normalized_message = message.lower() if isinstance(message, str) else ""
        if _filled(message) and not (
            any(ch.isdigit() for ch in message)
            or any(word in normalized_message for word in SIGNAL_WORDS)
        ):
            errors.append(f"{prefix}.message: must state a finding, not only name a topic")

        comparison_text = " ".join(
            str(view.get(key, "")) for key in ("message", "reason", "evidence_ref")
        ).lower()
        if view.get("comparison") is not None or any(hint in comparison_text for hint in COMPARISON_HINTS):
            _validate_comparison(view.get("comparison"), prefix, errors)

        relation = view.get("relation")
        primary_view = view.get("primary_view")
        if relation not in RELATIONS:
            errors.append(f"{prefix}.relation: unsupported relationship {relation!r}")
        elif primary_view not in allowed_views(relation):
            errors.append(f"{prefix}.primary_view: {primary_view!r} is not suitable for {relation!r}")

        rejected = view.get("rejected_alternatives")
        if not isinstance(rejected, list) or not rejected:
            errors.append(f"{prefix}.rejected_alternatives: record at least one rejected view and reason")
        else:
            for alt_index, alternative in enumerate(rejected):
                if not isinstance(alternative, dict) or not _filled(alternative.get("view")) or not _filled(alternative.get("reason")):
                    errors.append(f"{prefix}.rejected_alternatives[{alt_index}]: require view and reason")

        table_mode = view.get("table_mode")
        if table_mode not in TABLE_MODES:
            errors.append(f"{prefix}.table_mode: must be one of {sorted(TABLE_MODES)}")

        category_count = view.get("category_count", 0)
        measure_count = view.get("measure_count", 1)
        exact_lookup = view.get("exact_lookup", False)
        if isinstance(category_count, int) and primary_view == "pie" and category_count > 3:
            errors.append(f"{prefix}.primary_view: pie is limited to 2–3 categories")
        needs_analytical_table = exact_lookup is True or (
            isinstance(category_count, int) and category_count > 15
        ) or (isinstance(measure_count, int) and measure_count >= 4)
        if needs_analytical_table and table_mode not in {"companion", "primary"}:
            errors.append(f"{prefix}.table_mode: exact/high-density views require companion or primary")
        if primary_view == "table" and table_mode != "primary":
            errors.append(f"{prefix}.table_mode: a primary table view requires table_mode='primary'")
        if table_mode in {"companion", "primary"}:
            if not _filled(view.get("table_reason")):
                errors.append(f"{prefix}.table_reason: required for companion/primary tables")
            columns = view.get("table_columns")
            if not isinstance(columns, list) or len(columns) < 2 or not all(_filled(c) for c in columns):
                errors.append(f"{prefix}.table_columns: require at least two decision columns")

    findings = plan.get("findings")
    if not isinstance(findings, list):
        errors.append("findings: must be a list")
        findings = []
    if mode in {"decision_support", "monitoring"} and not any(
        isinstance(f, dict) and f.get("importance") == "major" for f in findings
    ):
        errors.append("findings: decision_support/monitoring requires at least one major finding")

    for index, finding in enumerate(findings):
        prefix = f"findings[{index}]"
        if not isinstance(finding, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        if finding.get("importance") not in {"major", "supporting"}:
            errors.append(f"{prefix}.importance: must be major or supporting")
        for key in ("id", "what", "baseline", "why", "so_what", "next_check"):
            if not _filled(finding.get(key)):
                errors.append(f"{prefix}.{key}: required non-empty string")
        if finding.get("why_status") not in WHY_STATUSES:
            errors.append(f"{prefix}.why_status: must be one of {sorted(WHY_STATUSES)}")
        for key in ("evidence_refs", "limitations"):
            value = finding.get(key)
            if not isinstance(value, list) or not value or not all(_filled(item) for item in value):
                errors.append(f"{prefix}.{key}: require at least one non-empty item")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="Path to analysis plan JSON")
    args = parser.parse_args()

    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read valid JSON: {exc}")
        return 1

    errors = validate_plan(plan)
    if errors:
        print(f"FAIL: {len(errors)} analysis expression issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: analysis expression plan is decision-ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
