"""Generate a concise executive brief from a report artifact."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ExecutiveBrief:
    source_path: str
    generated_at: str
    key_numbers: list[str] = field(default_factory=list)
    likely_conclusions: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。.!?？])\s+|\n+", text)
    return [part.strip(" -\t") for part in parts if part.strip(" -\t")]


def generate_brief(source_path: str, max_items: int = 5) -> ExecutiveBrief:
    path = Path(source_path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    sentences = _sentences(re.sub(r"<[^>]+>", " ", text))
    key_numbers = re.findall(r"(?<![\w.])-?\d+(?:\.\d+)?%?", text)[: max_items * 2]
    conclusion_keywords = ("结论", "发现", "增长", "下降", "异常", "提升", "降低", "贡献", "风险")
    action_keywords = ("建议", "行动", "下一步", "优化", "修复", "关注", "优先")
    caveat_keywords = ("限制", "口径", "样本", "假设", "缺失", "置信")

    def pick(keywords: tuple[str, ...]) -> list[str]:
        picked = [sentence for sentence in sentences if any(keyword in sentence for keyword in keywords)]
        return picked[:max_items]

    return ExecutiveBrief(
        source_path=str(path.resolve()),
        generated_at=datetime.now().isoformat(timespec="seconds"),
        key_numbers=key_numbers,
        likely_conclusions=pick(conclusion_keywords),
        action_items=pick(action_keywords),
        caveats=pick(caveat_keywords),
    )


def render_brief_markdown(brief: ExecutiveBrief) -> str:
    lines = [
        "# 高管摘要",
        "",
        f"- 来源: `{brief.source_path}`",
        f"- 生成时间: {brief.generated_at}",
        "",
        "## 关键数字",
        "",
    ]
    lines.extend(f"- {item}" for item in brief.key_numbers[:10] or ["未提取到关键数字。"])
    lines.extend(["", "## 主要结论", ""])
    lines.extend(f"- {item}" for item in brief.likely_conclusions or ["未提取到明确结论句。"])
    lines.extend(["", "## 行动建议", ""])
    lines.extend(f"- {item}" for item in brief.action_items or ["未提取到行动建议。"])
    lines.extend(["", "## 口径与限制", ""])
    lines.extend(f"- {item}" for item in brief.caveats or ["未提取到口径或限制说明。"])
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="从报告中生成高管摘要")
    parser.add_argument("source", help="报告或分析产物路径")
    parser.add_argument("--max-items", type=int, default=5)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", help="输出路径")
    args = parser.parse_args()

    brief = generate_brief(args.source, args.max_items)
    content = json.dumps(brief.to_dict(), ensure_ascii=False, indent=2) if args.format == "json" else render_brief_markdown(brief)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    print(content)


if __name__ == "__main__":  # pragma: no cover
    main()
