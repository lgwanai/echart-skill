import os
import sys
import zipfile


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_create_delivery_pack_writes_zip_and_manifest(tmp_path):
    from scripts.delivery_pack import create_delivery_pack

    report = tmp_path / "report.md"
    evidence = tmp_path / "evidence.md"
    report.write_text("# Report\n", encoding="utf-8")
    evidence.write_text("# Evidence\n", encoding="utf-8")
    output = tmp_path / "delivery.zip"

    zip_path, manifest = create_delivery_pack([str(report), str(evidence)], str(output))
    assert zip_path == output
    assert len(manifest.items) == 2
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert "manifest.json" in names
    assert "README.md" in names
    assert "report.md" in names

