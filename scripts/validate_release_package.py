#!/usr/bin/env python3
"""Validate that a packaged skill contains only reusable, non-local content."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import unicodedata
import zipfile
from pathlib import Path

FORBIDDEN_PATH_PATTERNS = (
    re.compile(r"(^|/)(?:queries|outputs|logs|dist|tmp|backup)(/|$)"),
    re.compile(r"(^|/)db_connections\.txt$"),
    re.compile(r"(^|/)project_(?:db|metrics|schema)_index\.json$"),
    re.compile(r"(^|/)(?:\.git|\.claude|\.planning|\.echart-skill)(/|$)"),
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

SKILLHUB_MAX_FILES = 200
# Use decimal MB, the stricter interpretation of the requested 6M limit.
SKILLHUB_MAX_BYTES = 6_000_000
TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".py",
    ".sh",
    ".js",
    ".css",
    ".html",
}


def validate_skillhub_files(files: dict[str, bytes], package_bytes: int) -> list[str]:
    """Check the actual decoded contents, not just extensions. No nested archives."""
    errors = []
    if len(files) > SKILLHUB_MAX_FILES:
        errors.append(f"SkillHub file count {len(files)} exceeds {SKILLHUB_MAX_FILES}")
    if package_bytes > SKILLHUB_MAX_BYTES:
        errors.append(
            f"SkillHub package size {package_bytes} exceeds {SKILLHUB_MAX_BYTES} bytes"
        )
    for name, payload in files.items():
        if Path(name).suffix.lower() not in TEXT_SUFFIXES and Path(name).name not in {
            "LICENSE",
            "NOTICE",
        }:
            errors.append(f"SkillHub non-text file type: {name}")
        try:
            text = payload.decode("utf-8")
            invisible = sorted({c for c in text if unicodedata.category(c) == "Cf"})
            if invisible:
                labels = ", ".join(
                    f'U+{ord(c):04X} {unicodedata.name(c, "FORMAT")}' for c in invisible
                )
                errors.append(
                    f"SkillHub invisible Unicode format characters in {name}: {labels}"
                )
            if any(
                (ord(c) < 32 and c not in "\t\n\r") or 127 <= ord(c) <= 159
                for c in text
            ):
                errors.append(f"SkillHub binary/control bytes in file: {name}")
        except UnicodeDecodeError:
            errors.append(f"SkillHub non-UTF-8/binary file: {name}")
    return errors


def validate_package(path: Path, profile: str = "standard") -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"package not found: {path}"]
    try:
        archive = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        return [f"not a valid zip archive: {path}"]

    with archive:
        names = archive.namelist()
        required = (
            {"SKILL.md", "bootstrap.py", "chart_guide.md", "runtime.zip"}
            if "runtime.zip" in names
            else {"SKILL.md", "scripts/validate_chart.py"}
        )
        missing = sorted(required - set(names))
        if missing:
            errors.append(f"missing required package files: {missing}")
        if profile == "skillhub":
            errors.extend(
                validate_skillhub_files(
                    {
                        item.filename: archive.read(item)
                        for item in archive.infolist()
                        if not item.is_dir()
                    },
                    path.stat().st_size,
                )
            )
        errors.extend(_inspect_archive(archive))
    return errors


def _inspect_archive(archive, prefix="", depth=0):
    errors = []
    names = archive.namelist()
    if len(names) != len(set(names)):
        errors.append(f"duplicate archive entries: {prefix}")
    if "runtime-manifest.json" in names:
        try:
            manifest = json.loads(archive.read("runtime-manifest.json"))
            if set(manifest) != set(names) - {"runtime-manifest.json"}:
                errors.append(f"runtime manifest file list differs: {prefix}")
            for name, checksum in manifest.items():
                if hashlib.sha256(archive.read(name)).hexdigest() != checksum:
                    errors.append(f"runtime checksum mismatch: {prefix}{name}")
        except (ValueError, KeyError, AttributeError):
            errors.append(f"invalid runtime manifest: {prefix}")
    for name in names:
        if Path(name).is_absolute() or ".." in Path(name).parts or "\\" in name:
            errors.append(f"unsafe archive path: {prefix}{name}")
            continue
        normalized = name
        while normalized.startswith("./"):
            normalized = normalized[2:]
        normalized = normalized.lstrip("/")
        if any(pattern.search(normalized) for pattern in FORBIDDEN_PATH_PATTERNS):
            errors.append(f"forbidden local/project path in package: {normalized}")
            continue
        if name.lower().endswith(".zip"):
            if depth >= 2:
                errors.append(f"excessively nested archive: {prefix}{name}")
                continue
            try:
                with zipfile.ZipFile(io.BytesIO(archive.read(name))) as nested:
                    if name == "runtime.zip" and not {
                        "runtime-manifest.json",
                        "SKILL.md",
                        "scripts/validate_chart.py",
                    } <= set(nested.namelist()):
                        errors.append("missing required portable runtime files")
                    errors.extend(
                        _inspect_archive(nested, prefix + name + "/", depth + 1)
                    )
            except zipfile.BadZipFile:
                errors.append(f"invalid nested archive: {prefix}{name}")
            continue
        if name.endswith("/") or not name.lower().endswith(
            (
                ".md",
                ".txt",
                ".json",
                ".yaml",
                ".yml",
                ".py",
                ".sh",
                ".js",
                ".css",
                ".html",
            )
        ):
            continue
        payload = archive.read(name)
        for pattern in FORBIDDEN_PROJECT_MARKERS:
            if pattern.search(payload):
                errors.append(f"project-specific marker in package file: {normalized}")
                break
        if PRIVATE_KEY_PATTERN.search(payload):
            errors.append(
                f"possible embedded private key in package file: {normalized}"
            )
            continue
        if name.lower().endswith((".json", ".yaml", ".yml", ".txt")):
            for pattern in CONFIG_SECRET_PATTERNS:
                if pattern.search(payload):
                    errors.append(
                        f"possible embedded credential in package file: {normalized}"
                    )
                    break
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument(
        "--profile", choices=["standard", "skillhub"], default="standard"
    )
    args = parser.parse_args()
    errors = validate_package(args.package, args.profile)
    if errors:
        print("INVALID release package")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: release package contains only reusable skill content")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
