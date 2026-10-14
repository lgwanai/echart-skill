import hashlib
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from scripts.build_skill_package import build, zip_bytes
from scripts.portable_bootstrap import prepare
from scripts.validate_release_package import validate_package

ROOT = Path(__file__).resolve().parents[1]


def test_four_file_package_extracts_and_compiles_without_repository(tmp_path):
    package = tmp_path / "portable.zip"
    build(ROOT, package, "portable")
    assert validate_package(package) == []
    install = tmp_path / "install"
    project = tmp_path / "project"
    project.mkdir()
    with zipfile.ZipFile(package) as archive:
        assert set(archive.namelist()) == {
            "SKILL.md",
            "chart_guide.md",
            "bootstrap.py",
            "runtime.zip",
        }
        archive.extractall(install)
    root = prepare(install / "runtime.zip", project / ".echart-runtime")
    assert not (root / "references/legacy_examples.zip").exists()
    (project / "rows.json").write_text('[{"region":"North","value":12}]')
    spec = {
        "charts": [
            {
                "id": "c1",
                "view": "bar",
                "title": "Revenue",
                "scope": "SUM revenue",
                "source": "q1",
                "query_hash": "hash1",
                "rows_path": "rows.json",
                "x": "region",
                "metrics": [{"field": "value", "name": "Revenue", "unit": "CNY"}],
            }
        ]
    }
    (project / "spec.json").write_text(json.dumps(spec))
    subprocess.run(
        [
            sys.executable,
            str(install / "bootstrap.py"),
            "chart_builder.py",
            "spec.json",
            "--output",
            "result.html",
        ],
        cwd=project,
        check=True,
        capture_output=True,
    )
    (project / "draft.json").write_text(
        json.dumps(
            {
                "queries": [
                    {"id": "q1", "query_hash": "hash1", "result_path": "rows.json"}
                ]
            }
        )
    )
    for args in [
        ("artifact_manifest.py", "bind", "result.html", "draft.json"),
        ("validate_delivery.py", "result.html"),
    ]:
        result = subprocess.run(
            [sys.executable, str(install / "bootstrap.py"), *args],
            cwd=project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    result = subprocess.run(
        [
            sys.executable,
            str(install / "bootstrap.py"),
            "chart_builder.py",
            "spec.json",
            "--output",
            "verified.html",
            "--evidence",
            "draft.json",
        ],
        cwd=project,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    previous = (project / "verified.html").read_bytes()
    # Valid chart data but invalid evidence must not replace the last good output.
    (project / "draft.json").write_text('{"queries":[]}')
    result = subprocess.run(
        [
            sys.executable,
            str(install / "bootstrap.py"),
            "chart_builder.py",
            "spec.json",
            "--output",
            "verified.html",
            "--evidence",
            "draft.json",
        ],
        cwd=project,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert (project / "verified.html").read_bytes() == previous


@pytest.mark.parametrize(
    "name,payload", [("../escape.py", b"bad"), ("good.py", b"tampered")]
)
def test_bootstrap_rejects_unsafe_or_tampered_runtime(tmp_path, name, payload):
    bundle = tmp_path / "runtime.zip"
    bundle.write_bytes(
        zip_bytes(
            {
                name: payload,
                "runtime-manifest.json": json.dumps(
                    {name: hashlib.sha256(b"good").hexdigest()}
                ).encode(),
            }
        )
    )
    with pytest.raises(ValueError):
        prepare(bundle, tmp_path / "cache")


def test_release_validator_checks_nested_content(tmp_path):
    package = tmp_path / "nested.zip"
    nested = zip_bytes({"../secret.txt": b"bad"})
    package.write_bytes(
        zip_bytes(
            {
                "SKILL.md": b"skill",
                "scripts/validate_chart.py": b"pass",
                "references/legacy_examples.zip": nested,
            }
        )
    )
    assert any("unsafe archive path" in error for error in validate_package(package))
