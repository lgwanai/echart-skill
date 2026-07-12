"""Evidence pack generation for BI artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.audit_report import _audit_log_path, _read_entries
from scripts.lineage_manager import LineageRecord, find_lineage
from scripts.metrics_manager import render_effective_metrics


@dataclass
class EvidencePack:
    artifact_path: str
    artifact_sha256: str
    generated_at: str
    lineage: list[dict[str, Any]] = field(default_factory=list)
    audit_entries: list[dict[str, Any]] = field(default_factory=list)
    effective_metrics: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _query_hashes(records: list[LineageRecord]) -> set[str]:
    result: set[str] = set()
    for record in records:
        result.update(record.query_hashes)
    return result


def build_evidence_pack(
    artifact_path: str,
    cwd: str | None = None,
    lineage_path: str = "",
    audit_log_path: str = "",
) -> EvidencePack:
    artifact = Path(artifact_path).resolve()
    if not artifact.exists():
        raise FileNotFoundError(f"artifact not found: {artifact}")

    lineage_records = find_lineage(str(artifact), path=lineage_path or None)
    hashes = _query_hashes(lineage_records)
    audit_entries = []
    for entry in _read_entries(_audit_log_path(audit_log_path)):
        query_hash = entry.get("q")
        if query_hash and query_hash in hashes:
            audit_entries.append(entry)

    notes = []
    if not lineage_records:
        notes.append("未找到该产物的血缘记录。")
    if hashes and not audit_entries:
        notes.append("血缘中存在 query hash，但审计日志未匹配到对应查询记录。")

    return EvidencePack(
        artifact_path=str(artifact),
        artifact_sha256=_sha256(artifact),
        generated_at=datetime.now().isoformat(timespec="seconds"),
        lineage=[record.to_dict() for record in lineage_records],
        audit_entries=audit_entries,
        effective_metrics=render_effective_metrics(cwd),
        notes=notes,
    )


def render_evidence_markdown(pack: EvidencePack) -> str:
    lines = [
        "# 证据包",
        "",
        f"- 产物: `{pack.artifact_path}`",
        f"- SHA256: `{pack.artifact_sha256}`",
        f"- 生成时间: {pack.generated_at}",
        f"- 血缘记录数: {len(pack.lineage)}",
        f"- 审计匹配数: {len(pack.audit_entries)}",
        "",
        "## 数据血缘",
        "",
    ]
    if pack.lineage:
        lines.append("| 时间 | 类型 | 来源表 | 字段 | Query Hash | 口径 |")
        lines.append("|---|---|---|---|---|---|")
        for item in pack.lineage:
            lines.append(
                f"| {item.get('created_at', '')} | {item.get('artifact_type', '')} | "
                f"{', '.join(item.get('source_tables', []))} | {', '.join(item.get('columns', []))} | "
                f"{', '.join(item.get('query_hashes', []))} | {', '.join(item.get('metric_scopes', []))} |"
            )
    else:
        lines.append("无。")

    lines.extend(["", "## 审计证据", ""])
    if pack.audit_entries:
        lines.append("| 时间 | 类型 | 表 | 行数 | 脱敏 | Query Hash |")
        lines.append("|---|---|---|---:|---|---|")
        for entry in pack.audit_entries:
            lines.append(
                f"| {entry.get('ts', '')} | {entry.get('typ', 'query')} | `{entry.get('tbl', '')}` | "
                f"{entry.get('n', 0)} | {entry.get('mask', '')} | `{entry.get('q', '')}` |"
            )
    else:
        lines.append("无。")

    lines.extend(["", "## 生效统计口径", "", pack.effective_metrics.strip(), ""])
    if pack.notes:
        lines.extend(["## 注意事项", ""])
        lines.extend(f"- {note}" for note in pack.notes)
        lines.append("")
    return "\n".join(lines)


def write_evidence_pack(pack: EvidencePack, output_path: str = "", output_format: str = "markdown") -> Path:
    if output_path:
        path = Path(output_path)
    else:
        out_dir = PROJECT_ROOT / "outputs" / "evidence"
        out_dir.mkdir(parents=True, exist_ok=True)
        suffix = "json" if output_format == "json" else "md"
        stem = Path(pack.artifact_path).stem
        path = out_dir / f"{stem}_evidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{suffix}"
    path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        path.write_text(json.dumps(pack.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        path.write_text(render_evidence_markdown(pack), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="为报告/Dashboard/图表生成证据包")
    parser.add_argument("artifact", help="产物路径")
    parser.add_argument("--cwd", help="用于解析项目级统计口径的目录")
    parser.add_argument("--lineage-path", default="", help="血缘 JSONL 路径")
    parser.add_argument("--audit-log", default="", help="审计日志路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", help="输出路径")
    parser.add_argument("--print", action="store_true", help="同时打印证据包")
    args = parser.parse_args()

    pack = build_evidence_pack(args.artifact, args.cwd, args.lineage_path, args.audit_log)
    path = write_evidence_pack(pack, args.output or "", args.format)
    if args.print:
        if args.format == "json":
            print(json.dumps(pack.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(render_evidence_markdown(pack))
    print(f"✅ 证据包已生成: {path}")


if __name__ == "__main__":  # pragma: no cover
    main()
