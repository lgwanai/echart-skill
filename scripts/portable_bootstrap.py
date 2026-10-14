#!/usr/bin/env python3
"""Expand checksum-verified bundled tools in the project; preserve working directory."""

import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path


def prepare(bundle, cache):
    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    destination = cache / digest[:16]
    with zipfile.ZipFile(bundle) as archive:
        manifest = json.loads(archive.read("runtime-manifest.json"))
        for name, expected in manifest.items():
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Unsafe bundle path")
            payload = archive.read(name)
            if hashlib.sha256(payload).hexdigest() != expected:
                raise ValueError(f"Bundle checksum mismatch: {name}")
            target = destination / relative
            if (
                not target.exists()
                or hashlib.sha256(target.read_bytes()).hexdigest() != expected
            ):
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
    return destination


if __name__ == "__main__":
    root = prepare(
        Path(__file__).with_name("runtime.zip"), Path.cwd() / ".echart-runtime"
    )
    if len(sys.argv) == 1:
        print(root)
    else:
        script = sys.argv[1]
        if (
            Path(script).name != script
            or not script.endswith(".py")
            or not (root / "scripts" / script).is_file()
        ):
            raise SystemExit("Pass a maintained script basename, e.g. chart_builder.py")
        os.execv(
            sys.executable,
            [sys.executable, str(root / "scripts" / script), *sys.argv[2:]],
        )
