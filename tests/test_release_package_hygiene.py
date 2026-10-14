import os
import subprocess
import zipfile
from pathlib import Path

from scripts.validate_release_package import validate_package


ROOT = Path(__file__).resolve().parents[1]


def test_packager_excludes_project_and_local_state(tmp_path: Path):
    package_name = "echart-skill-test.zip"
    env = os.environ.copy()
    env.update({"DIST_DIR": str(tmp_path), "PACKAGE_NAME": package_name})

    subprocess.run(["bash", str(ROOT / "package.sh")], cwd=ROOT, env=env, check=True)

    package = tmp_path / package_name
    assert validate_package(package) == []
    with zipfile.ZipFile(package) as archive:
        names = archive.namelist()
    assert not any(name.startswith("queries/") for name in names)
    assert "references/db_connections.txt" not in names
    assert not any(name.startswith(("outputs/", "logs/", ".git/")) for name in names)


def test_validator_rejects_project_specific_content(tmp_path: Path):
    package = tmp_path / "contaminated.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("SKILL.md", "---\nname: demo\n---\n凤悦 dashboard")
        archive.writestr("scripts/validate_chart.py", "pass\n")

    errors = validate_package(package)
    assert any("project-specific marker" in error for error in errors)


def test_validator_rejects_project_data_context_path(tmp_path: Path):
    package = tmp_path / "project-context.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("SKILL.md", "---\nname: demo\n---\n")
        archive.writestr("scripts/validate_chart.py", "pass\n")
        archive.writestr(".echart-skill/data_sources.json", '{"version": 1}')

    errors = validate_package(package)
    assert any("forbidden local/project path" in error for error in errors)
