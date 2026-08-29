#!/usr/bin/env python3
"""Validate that a packaged skill contains only reusable, non-local content."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path


FORBIDDEN_PATH_PATTERNS = (
    re.compile(r"(^|/)(?:queries|outputs|logs|dist|tmp|backup)(/|$)"),
    re.compile(r"(^|/)db_connections\.txt$"),
    re.compile(r"(^|/)project_(?:db|metrics|schema)_index\.json$"),
    re.compile(r"(^|/)(?:\.git|\.claude|\.planning)(/|$)"),
    re.compile(r"(^|/)workspace\.duckdb$"),
)

CONFIG_SECRET_PATTERNS = (
    re.compile(rb"postgres(?:ql)?://[^\s:/]+:[^\s@/]+@", re.IGNORECASE),
    re.compile(rb"mysql://[^\s:/]+:[^\s@/]+@", re.IGNORECASE),
    re.compile(rb"AKIA[0-9A-Z]{16}"),
)
PRIVATE_KEY_PATTERN = re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
FORBIDDEN_PROJECT_MARKERS = (
    re.compile(bytes.fromhex("e587a4e682a6")),
    re.compile(bytes.fromhex("e4ba9ae69cb5")),
    re.compile(rb"\b(?:" + b"feng" + b"yue|a" + b"tour)\b", re.IGNORECASE),
)


def validate_package(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"package not found: {path}"]
    try:
        archive = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        return [f"not a valid zip archive: {path}"]

    with archive:
        names = archive.namelist()
        required = {"SKILL.md", "scripts/validate_chart.py"}
        missing = sorted(required - set(names))
        if missing:
            errors.append(f"missing required package files: {missing}")
        for name in names:
            normalized = name.lstrip("./")
            if any(pattern.search(normalized) for pattern in FORBIDDEN_PATH_PATTERNS):
                errors.append(f"forbidden local/project path in package: {normalized}")
                continue
            if name.endswith("/") or not name.lower().endswith(
                (".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh", ".js", ".css", ".html")
            ):
                continue
            payload = archive.read(name)
            for pattern in FORBIDDEN_PROJECT_MARKERS:
                if pattern.search(payload):
                    errors.append(f"project-specific marker in package file: {normalized}")
                    break
            if PRIVATE_KEY_PATTERN.search(payload):
                errors.append(f"possible embedded private key in package file: {normalized}")
                continue
            if name.lower().endswith((".json", ".yaml", ".yml", ".txt")):
                for pattern in CONFIG_SECRET_PATTERNS:
                    if pattern.search(payload):
                        errors.append(f"possible embedded credential in package file: {normalized}")
                        break
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    errors = validate_package(args.package)
    if errors:
        print("INVALID release package")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: release package contains only reusable skill content")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
