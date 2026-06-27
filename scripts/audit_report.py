"""Audit command logging and daily audit report generation."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config_manager import get_config


def _audit_log_path(explicit_path: str = "") -> Path:
    path = explicit_path or get_config().privacy.audit_log_path
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = PROJECT_ROOT / resolved
    return resolved


def _parse_date(value: str | None) -> date:
    if not value:
        return datetime.now().date()
    return datetime.strptime(value, "%Y-%m-%d").date()


def _entry_date(entry: dict[str, Any]) -> date | None:
    raw = entry.get("ts") or entry.get("timestamp")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw)).date()
    except ValueError:
        return None


def _read_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(entry, dict):
                entries.append(entry)
    return entries


def log_command(command: str, cwd: str | None = None, status: str = "started", note: str = "", log_path: str = "") -> Path:
    """Append a command audit entry."""
    path = _audit_log_path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "typ": "command",
        "ts": datetime.now().isoformat(timespec="seconds"),
        "cmd": command,
        "cwd": str(Path(cwd or os.getcwd()).resolve()),
        "status": status,
        "note": note,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path


def filter_entries(entries: list[dict[str, Any]], start: date, days: int = 1) -> list[dict[str, Any]]:
    end = start + timedelta(days=days)
    result = []
    for entry in entries:
        entry_day = _entry_date(entry)
        if entry_day is not None and start <= entry_day < end:
            result.append(entry)
    return result


def render_report(entries: list[dict[str, Any]], report_date: date, days: int = 1) -> str:
    """Render a Markdown audit report for the selected date range."""
    end_date = report_date + timedelta(days=days - 1)
    title_date = str(report_date) if days == 1 else f"{report_date} 至 {end_date}"
    command_entries = [e for e in entries if e.get("typ") == "command"]
    query_entries = [e for e in entries if e.get("typ") != "command"]

    command_counter = Counter(e.get("cmd", "(unknown)").split()[0] for e in command_entries)
    table_counter = Counter(e.get("tbl", "(unknown)") for e in query_entries)

    lines = [
        f"# echart-skill 审计报告",
        "",
        f"- 日期范围: {title_date}",
        f"- 指令记录数: {len(command_entries)}",
        f"- 查询记录数: {len(query_entries)}",
        "",
        "## 指令概览",
        "",
    ]
    if command_counter:
        lines.append("| 指令前缀 | 次数 |")
        lines.append("|---|---:|")
        for name, count in command_counter.most_common():
            lines.append(f"| `{name}` | {count} |")
    else:
        lines.append("当天没有记录到指令。")

    lines.extend(["", "## 查询概览", ""])
    if table_counter:
        lines.append("| 表/结果 | 次数 |")
        lines.append("|---|---:|")
        for table, count in table_counter.most_common():
            lines.append(f"| `{table}` | {count} |")
    else:
        lines.append("当天没有记录到查询。")

    lines.extend(["", "## 指令明细", ""])
    if command_entries:
        lines.append("| 时间 | 状态 | 工作目录 | 指令 | 备注 |")
        lines.append("|---|---|---|---|---|")
        for entry in command_entries:
            lines.append(
                f"| {entry.get('ts', '')} | {entry.get('status', '')} | "
                f"`{entry.get('cwd', '')}` | `{entry.get('cmd', '')}` | {entry.get('note', '')} |"
            )
    else:
        lines.append("无。")

    lines.extend(["", "## 查询明细", ""])
    if query_entries:
        lines.append("| 时间 | 表/结果 | 列 | 行数 | 脱敏 | 最高级别 | 变更操作 | 拦截 | Query Hash |")
        lines.append("|---|---|---|---:|---|---|---|---|---|")
        for entry in query_entries:
            cols = ", ".join(entry.get("cols", [])) if isinstance(entry.get("cols"), list) else ""
            lines.append(
                f"| {entry.get('ts', '')} | `{entry.get('tbl', '')}` | {cols} | "
                f"{entry.get('n', 0)} | {entry.get('mask', '')} | {entry.get('lv', '')} | "
                f"{entry.get('mut', '')} | {entry.get('blk', '')} | `{entry.get('q', '')}` |"
            )
    else:
        lines.append("无。")

    lines.append("")
    return "\n".join(lines)


def write_report(report: str, report_date: date, output_path: str = "") -> Path:
    if output_path:
        path = Path(output_path)
    else:
        out_dir = PROJECT_ROOT / "outputs" / "audit"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"audit_{report_date.isoformat()}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="记录指令并生成审计报告")
    subparsers = parser.add_subparsers(dest="command", required=True)

    log_parser = subparsers.add_parser("log-command", help="记录一次用户指令")
    log_parser.add_argument("text", help="用户指令原文")
    log_parser.add_argument("--cwd", help="执行目录")
    log_parser.add_argument("--status", default="started", help="状态，如 started/completed/failed")
    log_parser.add_argument("--note", default="", help="备注")
    log_parser.add_argument("--log-path", default="", help="审计日志路径")

    report_parser = subparsers.add_parser("report", help="生成指定日期的审计报告")
    report_parser.add_argument("--date", help="日期，格式 YYYY-MM-DD；默认今天")
    report_parser.add_argument("--days", type=int, default=1, help="连续天数，默认 1")
    report_parser.add_argument("--output", help="输出 Markdown 路径")
    report_parser.add_argument("--log-path", default="", help="审计日志路径")
    report_parser.add_argument("--print", action="store_true", help="同时打印报告内容")

    args = parser.parse_args()
    if args.command == "log-command":
        path = log_command(args.text, cwd=args.cwd, status=args.status, note=args.note, log_path=args.log_path)
        print(f"✅ 已记录指令审计: {path}")
        return

    report_date = _parse_date(args.date)
    entries = filter_entries(_read_entries(_audit_log_path(args.log_path)), report_date, args.days)
    report = render_report(entries, report_date, args.days)
    path = write_report(report, report_date, args.output or "")
    if args.print:
        print(report)
    print(f"✅ 审计报告已生成: {path}")


if __name__ == "__main__":  # pragma: no cover
    main()
