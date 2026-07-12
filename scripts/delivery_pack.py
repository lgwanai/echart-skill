"""Create auditable local delivery packages for BI artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class DeliveryItem:
    source_path: str
    package_path: str
    sha256: str
    size_bytes: int


@dataclass
class DeliveryManifest:
    package_name: str
    generated_at: str
    items: list[DeliveryItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_file(path: str) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"delivery file not found: {p}")
    return p.resolve()


def create_delivery_pack(files: list[str], output: str = "") -> tuple[Path, DeliveryManifest]:
    if not files:
        raise ValueError("files must not be empty")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = PROJECT_ROOT / "outputs" / "delivery" / f"delivery_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    items: list[DeliveryItem] = []
    used_names: set[str] = set()

    for raw in files:
        src = _resolve_file(raw)
        name = src.name
        if name in used_names:
            name = f"{src.stem}_{len(used_names)}{src.suffix}"
        used_names.add(name)
        dest = out_dir / name
        shutil.copy2(src, dest)
        items.append(DeliveryItem(
            source_path=str(src),
            package_path=name,
            sha256=_sha256(dest),
            size_bytes=dest.stat().st_size,
        ))

    manifest = DeliveryManifest(
        package_name=out_dir.name,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        items=items,
    )
    (out_dir / "manifest.json").write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "README.md").write_text(render_manifest_markdown(manifest), encoding="utf-8")

    zip_path = Path(output) if output else out_dir.with_suffix(".zip")
    if not zip_path.is_absolute():
        zip_path = PROJECT_ROOT / zip_path
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in out_dir.rglob("*"):
            archive.write(file_path, file_path.relative_to(out_dir))
    return zip_path, manifest


def render_manifest_markdown(manifest: DeliveryManifest) -> str:
    lines = [
        "# BI 交付包清单",
        "",
        f"- 包名: `{manifest.package_name}`",
        f"- 生成时间: {manifest.generated_at}",
        f"- 文件数: {len(manifest.items)}",
        "",
        "| 文件 | 大小 | SHA256 | 来源 |",
        "|---|---:|---|---|",
    ]
    for item in manifest.items:
        lines.append(f"| `{item.package_path}` | {item.size_bytes} | `{item.sha256}` | `{item.source_path}` |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="打包报告、Dashboard、图表和证据包为本地交付包")
    parser.add_argument("files", nargs="+", help="要打包的文件")
    parser.add_argument("--output", help="输出 zip 路径")
    parser.add_argument("--json", action="store_true", help="输出 manifest JSON")
    args = parser.parse_args()

    zip_path, manifest = create_delivery_pack(args.files, args.output or "")
    if args.json:
        print(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_manifest_markdown(manifest))
    print(f"✅ BI 交付包已生成: {zip_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
