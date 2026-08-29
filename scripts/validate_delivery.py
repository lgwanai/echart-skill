#!/usr/bin/env python3
"""Run the complete static, governance, and browser quality gate for HTML."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from scripts.browser_smoke_test import run_smoke_test
    from scripts.validate_accessibility_performance import validate_accessibility_performance
    from scripts.validate_chart import validate as validate_chart
    from scripts.validate_output_quality import validate_artifact
except ModuleNotFoundError:
    from browser_smoke_test import run_smoke_test
    from validate_accessibility_performance import validate_accessibility_performance
    from validate_chart import validate as validate_chart
    from validate_output_quality import validate_artifact


def validate_delivery(
    html: Path,
    *,
    require_browser: bool = True,
    browser_report: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    if validate_chart(str(html)) != 0:
        errors.append("static chart/dashboard validation failed")
    errors.extend(validate_artifact(html, "html"))
    errors.extend(validate_accessibility_performance(html))
    browser_code, report = run_smoke_test(html)
    if browser_report:
        browser_report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    if browser_code == 1:
        errors.extend(f"browser: {message}" for message in report.get("errors", []))
    elif browser_code == 2 and require_browser:
        errors.append("browser: Playwright Chromium runtime unavailable")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument(
        "--allow-static-only",
        action="store_true",
        help="Permit delivery when no browser runtime is available; browser failures still block.",
    )
    parser.add_argument("--browser-report", type=Path)
    args = parser.parse_args()
    errors = validate_delivery(
        args.html,
        require_browser=not args.allow_static_only,
        browser_report=args.browser_report,
    )
    if errors:
        print("FAIL: delivery quality gate rejected the artifact")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: static, governance, and live-browser delivery gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
