#!/usr/bin/env python3
"""Recommend chart expressions from a machine-readable capability catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "references/chart_capabilities.json"


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def allowed_views(relation: str) -> set[str]:
    relation_spec = load_catalog().get("relations", {}).get(relation, {})
    return set(relation_spec.get("allowed", []))


def recommend_view(request: dict[str, Any]) -> dict[str, Any]:
    catalog = load_catalog()
    relation = request.get("relation")
    relation_spec = catalog.get("relations", {}).get(relation)
    if not relation_spec:
        raise ValueError(f"unsupported relation: {relation!r}")
    category_count = request.get("category_count", 0)
    roles = set(request.get("roles", []))
    candidates = []
    for view in relation_spec["allowed"]:
        spec = catalog["views"][view]
        reasons: list[str] = []
        max_categories = spec.get("max_categories")
        if isinstance(max_categories, int) and isinstance(category_count, int) and category_count > max_categories:
            reasons.append(f"category_count {category_count} exceeds {max_categories}")
        missing_roles = [role for role in spec.get("requires", []) if role not in roles]
        if missing_roles:
            reasons.append(f"missing roles {missing_roles}")
        score = 100 - relation_spec["preferred"].index(view) * 10 if view in relation_spec["preferred"] else 60
        if reasons:
            score = 0
        candidates.append({
            "view": view,
            "score": score,
            "eligible": not reasons,
            "reasons": reasons,
            "recipe": spec.get("recipe"),
            "accessible_fallback": spec.get("accessible_fallback"),
        })
    eligible = sorted((item for item in candidates if item["eligible"]), key=lambda item: -item["score"])
    exact_lookup = request.get("exact_lookup") is True
    measure_count = request.get("measure_count", 1)
    table_mode = "companion" if exact_lookup or category_count > 15 or measure_count >= 4 else "source_toggle"
    if not eligible:
        table_mode = "primary"
    return {
        "relation": relation,
        "selected": eligible[0] if eligible else {"view": "table", "score": 100, "eligible": True},
        "alternatives": eligible[1:3],
        "rejected": [item for item in candidates if not item["eligible"]],
        "table_mode": table_mode,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path, help="JSON view request")
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    print(json.dumps(recommend_view(request), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
