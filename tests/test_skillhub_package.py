import json
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

import pytest

from scripts.build_skill_package import build, SKILLHUB_RECIPES
from scripts.validate_release_package import validate_package, validate_skillhub_files

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def packaged(tmp_path_factory):
    base = tmp_path_factory.mktemp("skillhub")
    output = base / "skillhub.zip"
    build(ROOT, output, "skillhub")
    install = base / "skill"
    with zipfile.ZipFile(output) as archive:
        archive.extractall(install)
    return output, install


def test_upload_limits_and_text_only_content(packaged):
    output, install = packaged
    assert validate_package(output, "skillhub") == []
    files = [p for p in install.rglob("*") if p.is_file()]
    assert len(files) <= 200
    assert output.stat().st_size <= 6_000_000
    assert not list(install.rglob("*.zip"))
    assert not (install / "bootstrap.py").exists()
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert not any(unicodedata.category(c) == "Cf" for c in text), path
    skill = (install / "SKILL.md").read_text()
    assert "references/commands.md" in skill
    assert "commands/echart/" not in skill
    commands = (install / "references/commands.md").read_text()
    for path in (ROOT / "commands/echart").glob("*.md"):
        assert f'<a id="{path.stem}"></a>' in commands
    with zipfile.ZipFile(ROOT / "references/legacy_examples.zip") as archive:
        for name in SKILLHUB_RECIPES:
            assert (
                install / "references/examples" / name
            ).read_bytes() == archive.read(name)


@pytest.mark.parametrize(
    "files,size,reason",
    [
        ({f"{i}.md": b"ok" for i in range(201)}, 1, "file count"),
        ({"SKILL.md": b"ok"}, 6_000_001, "package size"),
        ({"nested.zip": b"PK\x03\x04"}, 100, "non-text file type"),
        ({"disguised.md": b"\x89PNG\x00"}, 100, "binary"),
        ({"control.js": b'var x="\x01";'}, 100, "control"),
        ({"note.md": "soft\u00adhyphen".encode()}, 100, "U+00AD SOFT HYPHEN"),
        ({"note.md": "zero\u200dwidth".encode()}, 100, "U+200D ZERO WIDTH JOINER"),
        (
            {"sample.py": "# direction\u202e".encode()},
            100,
            "U+202E RIGHT-TO-LEFT OVERRIDE",
        ),
    ],
)
def test_skillhub_gate_rejects_invalid_payloads(files, size, reason):
    assert any(reason in e for e in validate_skillhub_files(files, size))


def test_asset_normalization_preserves_maps_and_pdf(packaged):
    _, install = packaged
    # Parse every packaged JS, then compare actual map registrations and PDF bytes
    # after Unicode escaping. This is more than a text/syntax-only equivalence check.
    script = r"""
const fs=require('fs'), path=require('path'), vm=require('vm'), assert=require('assert');
const [original, packed]=process.argv.slice(1);
const echarts=require(path.join(original,'assets/echarts/echarts.min.js'));
let maps=0;
for (const sub of ['echarts','dashboard']) {
  for (const name of fs.readdirSync(path.join(packed,'assets',sub))) {
    if (!name.endsWith('.js')) continue;
    const rel=path.join('assets',sub,name);
    const before=fs.readFileSync(path.join(original,rel),'utf8');
    const after=fs.readFileSync(path.join(packed,rel),'utf8');
    new vm.Script(after, {filename:rel});
    if (before===after || name==='jspdf.umd.min.js') continue;
    function registered(code) {
      const result=[];
      vm.runInNewContext(code,{echarts:{registerMap(...args){result.push(args);}}, console});
      assert(result.length>0);
      for (const args of result) echarts.parseGeoJSON(args[1]);
      return JSON.stringify(result);
    }
    assert.strictEqual(registered(before), registered(after),rel);
    maps++;
  }
}
function pdf(root, encrypted) {
  const {jsPDF}=require(path.join(root,'assets/dashboard/jspdf.umd.min.js'));
  const doc=new jsPDF(encrypted ? {encryption:{userPassword:'test',ownerPassword:'test-owner'}} : {});
  doc.setCreationDate(new Date('2026-01-01T00:00:00Z'));
  doc.setFileId('0123456789ABCDEF0123456789ABCDEF');
  doc.text('SkillHub quality check',10,10);
  return doc.output();
}
assert.strictEqual(pdf(original,false),pdf(packed,false));
assert.strictEqual(pdf(original,true),pdf(packed,true));
assert(maps>0);
console.log('map assets checked:',maps);
"""
    result = subprocess.run(
        ["node", "-e", script, str(ROOT), str(install)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_unpacked_skill_generates_verified_chart(packaged, tmp_path):
    _, install = packaged
    (tmp_path / "rows.json").write_text(
        '[{"region":"North","value":10.0},{"region":"South","value":20.5}]'
    )
    chart = dict(
        id="c1",
        view="bar",
        title="Revenue",
        scope="SUM revenue per region",
        source="q1",
        query_hash="q1hash",
        rows_path="rows.json",
        x="region",
        metrics=[dict(field="value", name="Revenue", unit="CNY")],
    )
    (tmp_path / "spec.json").write_text(json.dumps({"charts": [chart]}))
    (tmp_path / "evidence.json").write_text(
        json.dumps(
            {
                "queries": [
                    {"id": "q1", "query_hash": "q1hash", "result_path": "rows.json"}
                ]
            }
        )
    )
    result = subprocess.run(
        [
            sys.executable,
            str(install / "scripts/chart_builder.py"),
            "spec.json",
            "--output",
            "verified.html",
            "--evidence",
            "evidence.json",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "verified.html").is_file()
    # The archive-free reference accessor still serves legacy report dependencies.
    result = subprocess.run(
        [
            sys.executable,
            str(install / "scripts/reference_assets.py"),
            "get",
            "geo-map-scatter",
            "--json",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["content"]
