#!/usr/bin/env python3
"""Losslessly archive historical demos with a small searchable catalog."""

import hashlib
import json
import zipfile
from pathlib import Path


def pack(root):
    source = root / "references/examples"
    target = root / "references/legacy_examples.zip"
    files = sorted(p for p in source.glob("*.md") if p.name != "INDEX.md")
    if not files:
        raise ValueError("No loose recipes to archive")
    if target.exists():
        raise ValueError("Archive exists; refusing to overwrite historical recipes")
    catalog = {}
    with zipfile.ZipFile(
        target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in files:
            payload = path.read_bytes()
            catalog[path.name] = {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "size": len(payload),
                "head": "\n".join(payload.decode("utf-8").splitlines()[:35])[:1800],
            }
            archive.writestr(path.name, payload)
        archive.writestr("catalog.json", json.dumps(catalog, ensure_ascii=False))
    with zipfile.ZipFile(target) as archive:
        for path in files:
            assert archive.read(path.name) == path.read_bytes(), path
    return {
        "archive": str(target),
        "files": len(files),
        "original_bytes": sum(p.stat().st_size for p in files),
        "archive_bytes": target.stat().st_size,
    }


if __name__ == "__main__":
    print(json.dumps(pack(Path(__file__).resolve().parents[1]), indent=2))
