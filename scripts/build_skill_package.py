#!/usr/bin/env python3
"""Build full, portable, or text-only SkillHub skill distributions."""

import argparse
import hashlib
import io
import json
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {
    "SKILL.md",
    "README.md",
    "README_EN.md",
    "pyproject.toml",
    "requirements.txt",
    "requirements-core.txt",
    "requirements-optional.txt",
    "database.py",
    "logging_config.py",
    "validators.py",
    "LICENSE",
    "NOTICE",
}
TREES = {"assets", "commands", "references", "scripts", "workflow_specs"}

SKILLHUB_RECIPES = (
    "bar-simple.md",
    "line-simple.md",
    "pie-simple.md",
    "geo-map-scatter.md",
)
SKILLHUB_EXCLUDE = {
    "README.md",
    "README_EN.md",
    "references/legacy_examples.zip",
    "scripts/build_skill_package.py",
    "scripts/pack_recipes.py",
    "scripts/portable_bootstrap.py",
    "scripts/install_claude_commands.py",
    "scripts/download_wheels.sh",
    "scripts/update_skill.py",
    "scripts/gen_weekly_report.py",
}


def expand_map_assets(files, root):
    """Use the bundled ECharts decoder at build time; emit numeric GeoJSON.

    Only trusted repository map assets are evaluated, never project/user scripts.
    Node is a publisher build dependency; the output needs no extraction step.
    """
    maps = {
        name: data.decode("utf-8")
        for name, data in files.items()
        if name.startswith("assets/echarts/")
        and name.endswith(".js")
        and not Path(name).name.startswith("echarts")
        and b"UTF8Encoding" in data
    }
    script = r"""
const fs=require('fs'), vm=require('vm');
const echarts=require(process.argv[1]);
const maps=JSON.parse(fs.readFileSync(0,'utf8')), result={};
for (const [name, source] of Object.entries(maps)) {
  const registrations=[];
  vm.runInNewContext(source, {echarts:{registerMap(...args){
    echarts.parseGeoJSON(args[1]);
    registrations.push(args);
  }}}, {filename:name, timeout:5000});
  if (!registrations.length) throw new Error('No map registration: '+name);
  result[name]=registrations;
}
process.stdout.write(JSON.stringify(result));
"""
    result = subprocess.run(
        ["node", "-e", script, str((root / "assets/echarts/echarts.min.js").resolve())],
        input=json.dumps(maps),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode:
        raise ValueError("Map expansion failed: " + result.stderr)
    for name, registrations in json.loads(result.stdout).items():
        # Preserve copyright/license comments from the source asset.
        comments = "\n".join(re.findall(r"/\*.*?\*/", maps[name], flags=re.S))
        calls = "\n".join(
            "echarts.registerMap("
            + ",".join(
                json.dumps(
                    arg, ensure_ascii=False, separators=(",", ":"), allow_nan=False
                ).replace("<", "\\u003c")
                for arg in args
            )
            + ");"
            for args in registrations
        )
        wrapper = """\n(function(root,factory){
if(typeof define==='function' && define.amd){define(['echarts'],factory);}
else if(typeof module==='object' && module.exports){factory(require('echarts'));}
else{factory(root.echarts);}
})(this,function(echarts){
if(!echarts) throw new Error('Load ECharts before map assets');
"""
        files[name] = (comments + wrapper + calls + "\n});\n").encode("utf-8")


def skillhub_payloads(root):
    """Consolidate documentation; retain engines, local assets, and quality gates."""
    original = payloads(root)
    files = {
        n: b
        for n, b in original.items()
        if n not in SKILLHUB_EXCLUDE and not n.startswith("commands/")
    }
    commands = [
        (n, b)
        for n, b in sorted(original.items())
        if n.startswith("commands/") and n.endswith(".md")
    ]
    sections = [
        "# Command reference (SkillHub)\n\nSearch the heading for the requested command. These are instructions, not installed slash-command registrations.\n"
    ]
    for name, data in commands:
        sections.append(
            f'\n<a id="{Path(name).stem}"></a>\n\n## {Path(name).stem}\n\n'
            + data.decode("utf-8")
        )
    files["references/commands.md"] = "\n".join(sections).encode("utf-8")
    # Keep the four dependencies used by the legacy report engine as real text.
    with zipfile.ZipFile(root / "references/legacy_examples.zip") as archive:
        for name in SKILLHUB_RECIPES:
            local = root / "references/examples" / name
            files[f"references/examples/{name}"] = (
                local.read_bytes() if local.is_file() else archive.read(name)
            )
    distribution = """# SkillHub distribution

This distribution is text-only: no nested ZIP, binary runtime, encoded archive,
or extraction bootstrap. Use the scripts directly. Run from the user's project
directory, supplying absolute paths to scripts in the installed skill directory.
Keep project data/configuration outside the skill.

Included: common-chart compiler, query/data-governance tools, all delivery gates,
report/dashboard workflows, local ECharts/GL/map/PDF JavaScript assets, and four
plain Markdown recipes needed by the legacy report engine. Command instructions
are consolidated in references/commands.md; no platform-specific command installer.
Excluded: the remaining historical demos, repository/release maintenance helpers,
and duplicated README files. Missing specialized demos are not bundled capabilities;
do not invent their contents or substitute a different chart meaning.

Python dependencies remain in requirements*.txt. Real rendering verification needs
Node.js, Playwright and Chromium supplied by the host; no binary dependency is
included. If unavailable, report unverified status, never claim a successful render.
All correctness, aligned-period, evidence and browser checks remain mandatory.

Only the outer upload ZIP is compressed. The publisher checks <=200 files, <=6,000,000
bytes compressed, and UTF-8 text with no binary control bytes for every member.
These checks implement the requested constraints, not a guarantee of marketplace approval.
"""
    files["references/distribution.md"] = distribution.encode("utf-8")
    index = """# Chart entry point (SkillHub)

Read `references/chart_guide.md` first; use `scripts/chart_builder.py` for common views.
Only these historical recipes are included as plain Markdown:
"""
    index += "\n".join(f"- `{name}`" for name in SKILLHUB_RECIPES)
    index += "\n\nUse `scripts/reference_assets.py list/get` to retrieve them. Other demos and the historical ZIP are not included. Demo instructions never override the chart guide or delivery gates.\n"
    files["references/examples/INDEX.md"] = index.encode("utf-8")
    skill = files["SKILL.md"].decode("utf-8")
    skill = skill.split("## Release hygiene")[0]
    skill = skill.replace(
        "## Required pipeline",
        "## SkillHub package\n\nRead `references/distribution.md` for included assets and host dependencies, and `references/security_review.md` before execution.\nUse absolute script paths from the user project directory; no bootstrap is needed.\n\n## Required pipeline",
    )
    skill = skill.replace(
        "For specialized views, retrieve one archived reference through",
        "For specialized views, first check the bundled recipe index; retrieve available references through",
    )
    files["SKILL.md"] = skill.encode("utf-8")
    guide = (
        files["references/chart_guide.md"]
        .decode("utf-8")
        .split("## Specialized views")[0]
    )
    guide += """## Specialized views (SkillHub)

Read `references/examples/INDEX.md` for the four included plain-text recipes.
The legacy report engine's recipe dependencies are included. Other historical
examples are omitted; ECharts GL and local map assets remain as JavaScript text.
Do not silently substitute a chart when a required example/dependency is absent.
Historical demo arrays are not production data: use actual query results, mark
every custom chart root `data-echart-chart`, and run the same delivery gates.
"""
    files["references/chart_guide.md"] = guide.encode("utf-8")
    expand_map_assets(files, root)
    # Redirect all command-document references after consolidation.
    for name, data in list(files.items()):
        if name.endswith(".md"):
            text = data.decode("utf-8").replace(
                "commands/echart/*.md", "references/commands.md"
            )
            text = re.sub(
                r"commands/echart/([A-Za-z0-9_-]+)\.md",
                r"references/commands.md#\1",
                text,
            )
            files[name] = text.encode("utf-8")
        elif name.endswith(".js"):
            source = data.decode("utf-8")
            # Keep original vendor assets untouched; escape literal string controls
            # in the SkillHub distribution so scanners recognize these as text.
            text = re.sub(
                r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]",
                lambda m: f"\\u{ord(m.group()):04x}",
                source,
            )
            files[name] = text.encode("utf-8")
    return files


def payloads(root, portable=False):
    result = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        name = relative.as_posix()
        if name not in ROOT_FILES and relative.parts[0] not in TREES:
            continue
        if any(p.startswith(".") or p in {"__pycache__", "logs", "outputs", "queries", "dist", "tmp", "backup"} for p in relative.parts):
            continue
        if (
            path.suffix in {".pyc", ".pyo", ".tmp", ".duckdb", ".log"}
            or path.name == "db_connections.txt"
            or path.name.startswith("project_")
            and path.name.endswith("_index.json")
        ):
            continue
        if name in {
            "references/metrics.md",
            "scripts/install.bat",
            "scripts/install.sh",
        }:
            continue
        if portable and name in {
            "references/legacy_examples.zip",
            "assets/echarts/echarts-gl.min.js",
        }:
            continue
        result[name] = path.read_bytes()
    return result


def zip_bytes(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, payload in sorted(files.items()):
            entry = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, payload)
    return buffer.getvalue()


def build(root, output, mode="full"):
    if mode not in {"full", "portable", "skillhub"}:
        raise ValueError(f"Unknown distribution mode: {mode}")
    files = payloads(root, portable=mode == "portable")
    if mode == "skillhub":
        files = skillhub_payloads(root)
    if mode == "portable":
        files["runtime-manifest.json"] = json.dumps(
            {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
            sort_keys=True,
        ).encode()
        runtime = zip_bytes(files)
        entry = """---
name: echart-skill
description: 用本地 SQL 分析项目数据，生成离线 ECharts 图表并逐图验证数据与浏览器渲染。
---
# EChart portable skill

First run `python /absolute/path/to/bootstrap.py` FROM THE USER PROJECT directory.
It prints the checksum-verified runtime path. Read its SKILL.md and routed files.
Use absolute paths to its scripts while preserving project cwd for data/config.
Python dependencies in requirements files and Node/Playwright/Chromium are needed.

Read chart_guide.md. Compile common charts from actual query results, bind evidence
and run validate_delivery.py. Browser absence means unverified, not successful.
Review meaning and labels as well as runtime checks. Specialized historical
examples and ECharts GL are in the full distribution; never silently change
chart meaning to avoid an unavailable dependency. Everything else runs offline.
"""
        files = {
            "SKILL.md": entry.encode(),
            "chart_guide.md": (root / "references/chart_guide.md").read_bytes(),
            "bootstrap.py": (root / "scripts/portable_bootstrap.py").read_bytes(),
            "runtime.zip": runtime,
        }
    packed = zip_bytes(files)
    if mode == "skillhub":
        try:
            from scripts.validate_release_package import validate_skillhub_files
        except ModuleNotFoundError:
            from validate_release_package import validate_skillhub_files
        errors = validate_skillhub_files(files, len(packed))
        if errors:
            raise ValueError("\n".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(packed)
    return {
        "mode": mode,
        "files": len(files),
        "uncompressed_bytes": sum(map(len, files.values())),
        "zip_bytes": output.stat().st_size,
        "output": str(output),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode", choices=["full", "portable", "skillhub"], default="full"
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(ROOT, args.output, args.mode), indent=2))
