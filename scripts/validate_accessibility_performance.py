#!/usr/bin/env python3
"""Validate baseline accessibility and performance invariants for HTML BI artifacts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MAX_HTML_BYTES = 15 * 1024 * 1024


def validate_accessibility_performance(path: Path) -> list[str]:
    errors: list[str] = []
    content = path.read_text(encoding="utf-8", errors="ignore")
    # Vendor JavaScript contains HTML/CSS examples, not actual page elements.
    markup = re.sub(r"<script\b[^>]*>.*?</script\s*>", "", content, flags=re.I | re.S)
    lower = content.lower()
    size = path.stat().st_size
    if size > MAX_HTML_BYTES:
        errors.append(f"PERFORMANCE: HTML is {size} bytes; maximum is {MAX_HTML_BYTES}")
    if "echarts.init" in content:
        has_accessible_chart = bool(
            re.search(r"\baria\s*:\s*\{[^{}]*\benabled\s*:\s*true", content, re.IGNORECASE | re.DOTALL)
            or re.search(r"\baria-label\s*=", content, re.IGNORECASE)
            or re.search(r"\baria-labelledby\s*=", content, re.IGNORECASE)
        )
        if not has_accessible_chart:
            errors.append(
                "ACCESSIBILITY: ECharts output needs aria.enabled=true or an aria-label/aria-labelledby chart name"
            )
    if re.search(r"<(?:img|area)\b(?![^>]*\balt\s*=)[^>]*>", markup, re.IGNORECASE):
        errors.append("ACCESSIBILITY: image/area element is missing alt text")
    if "<table" in lower and "<th" not in lower:
        errors.append("ACCESSIBILITY: data table has no header cells")
    if re.search(r"<button\b[^>]*>\s*</button>", content, re.IGNORECASE):
        errors.append("ACCESSIBILITY: empty button has no accessible name")
    has_animation = bool(re.search(r"(?:@keyframes|\banimation\s*:)", markup, re.IGNORECASE))
    if has_animation and "prefers-reduced-motion" not in lower:
        errors.append("ACCESSIBILITY: animated page lacks prefers-reduced-motion fallback")
    if re.search(r"user-scalable\s*=\s*no|maximum-scale\s*=\s*1", lower):
        errors.append("ACCESSIBILITY: viewport must not disable user zoom")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    args = parser.parse_args()
    errors = validate_accessibility_performance(args.html)
    if errors:
        print("FAIL: accessibility/performance gate rejected the artifact")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: accessibility/performance baseline satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
