#!/usr/bin/env python3
"""Render a local HTML artifact in Chromium and verify live chart surfaces."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/browser_smoke_runner.js"


def _candidate_node_paths() -> list[Path]:
    candidates: list[Path] = []
    if executable := shutil.which("node"):
        candidates.append(Path(executable))
    candidates.extend(
        Path.home().glob(
            ".cache/codex-runtimes/*/dependencies/node/bin/node"
        )
    )
    return list(dict.fromkeys(candidates))


def _candidate_node_modules() -> list[Path | None]:
    candidates: list[Path | None] = [
        Path(value) for value in os.environ.get("NODE_PATH", "").split(os.pathsep) if value
    ]
    candidates.append(None)
    candidates.extend(
        Path.home().glob(
            ".cache/codex-runtimes/*/dependencies/node/node_modules"
        )
    )
    return list(dict.fromkeys(candidates))


def _browser_executable(node: Path, modules: Path | None) -> Path | None:
    env = os.environ.copy()
    if modules:
        env["NODE_PATH"] = str(modules)
    result = subprocess.run(
        [str(node), "-e", "process.stdout.write(require('playwright').chromium.executablePath())"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    bundled = Path(result.stdout) if result.returncode == 0 and result.stdout else None
    candidates = [
        bundled,
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ]
    return next((path for path in candidates if path and path.is_file()), None)


def find_playwright_runtime() -> tuple[Path, Path | None, Path] | None:
    for node in _candidate_node_paths():
        for modules in _candidate_node_modules():
            env = os.environ.copy()
            if modules:
                env["NODE_PATH"] = str(modules)
            check = subprocess.run(
                [str(node), "-e", "require.resolve('playwright')"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if check.returncode == 0:
                browser = _browser_executable(node, modules)
                if browser:
                    return node, modules, browser
    return None


def run_smoke_test(
    html_path: Path,
    *,
    timeout_ms: int = 15000,
    screenshot: Path | None = None,
) -> tuple[int, dict]:
    runtime = find_playwright_runtime()
    if runtime is None:
        return 2, {
            "ok": False,
            "skipped": True,
            "errors": ["Node.js + Playwright Chromium runtime is unavailable"],
        }
    node, modules, browser = runtime
    env = os.environ.copy()
    if modules:
        env["NODE_PATH"] = str(modules)
    env["ECHART_SMOKE_BROWSER"] = str(browser)
    command = [str(node), str(RUNNER), str(html_path.resolve()), str(timeout_ms)]
    if screenshot:
        command.append(str(screenshot.resolve()))
    try:
        result = subprocess.run(command, env=env, capture_output=True, text=True, check=False,
                                timeout=max(20, timeout_ms / 1000 + 15))
    except subprocess.TimeoutExpired:
        return 1, {"ok": False, "errors": ["browser process timed out (possible infinite JavaScript loop)"]}
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        report = {"ok": False, "errors": [result.stderr or result.stdout or "browser runner failed"]}
    return result.returncode, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--timeout-ms", type=int, default=15000)
    parser.add_argument("--screenshot", type=Path)
    parser.add_argument("--require-browser", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.html.is_file():
        print(f"FAIL: HTML not found: {args.html}")
        return 1
    code, report = run_smoke_test(
        args.html,
        timeout_ms=args.timeout_ms,
        screenshot=args.screenshot,
    )
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if code == 2 and not args.require_browser:
        return 0
    return 1 if code else 0


if __name__ == "__main__":
    raise SystemExit(main())
