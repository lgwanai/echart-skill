"""Manage statistical scope and business metric definitions.

Definitions can be stored globally for the skill or project-locally for a
specific working directory. Project definitions are effective only when the
current execution directory is inside the recorded project directory.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
GLOBAL_METRICS_PATH = PROJECT_ROOT / "references" / "metrics.md"
PROJECT_INDEX_PATH = PROJECT_ROOT / "references" / "project_metrics_index.json"
PROJECT_METRICS_DIRNAME = ".echart-skill"
PROJECT_METRICS_FILENAME = "metrics.md"


@dataclass
class MetricDefinition:
    name: str
    description: str
    level: str
    file_path: str
    project_dir: str = ""
    created_at: str = ""


@dataclass
class MetricValidationIssue:
    severity: str
    metric_name: str
    source_path: str
    message: str
    recommendation: str


def _resolve_path(file_path: str | os.PathLike[str]) -> Path:
    path = Path(file_path)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _init_metrics_file(path: Path, title: str, project_dir: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    lines = [
        f"# {title}",
        "",
        "此文件记录核心统计口径和业务指标定义，作为后续生成 SQL、报告和 Dashboard 的口径上下文。",
        "",
    ]
    if project_dir:
        lines.extend([
            f"**项目目录**: `{project_dir}`",
            "",
            "仅当当前执行目录位于该项目目录下时，本文件口径才生效。",
            "",
        ])
    lines.append("---")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _append_definition(path: Path, metric_name: str, metric_description: str, level: str, project_dir: str = "") -> MetricDefinition:
    title = "数据统计口径 (Metrics Definitions)" if level == "global" else "项目统计口径 (Project Metrics Definitions)"
    _init_metrics_file(path, title, project_dir)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"## {metric_name}\n\n")
        handle.write(f"**级别**: {level}\n\n")
        if project_dir:
            handle.write(f"**项目目录**: `{project_dir}`\n\n")
        handle.write(f"**定义/描述**: {metric_description}\n\n")
        handle.write(f"*- 记录时间: {timestamp}*\n\n")
        handle.write("---\n\n")
    return MetricDefinition(
        name=metric_name,
        description=metric_description,
        level=level,
        file_path=str(path),
        project_dir=project_dir,
        created_at=timestamp,
    )


def _load_project_index() -> list[dict]:
    if not PROJECT_INDEX_PATH.exists():
        return []
    try:
        data = json.loads(PROJECT_INDEX_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def _save_project_index(items: list[dict]) -> None:
    PROJECT_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROJECT_INDEX_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def _record_project(project_dir: Path, metrics_path: Path) -> None:
    project_dir = project_dir.resolve()
    metrics_path = metrics_path.resolve()
    items = _load_project_index()
    record = {
        "project_dir": str(project_dir),
        "metrics_path": str(metrics_path),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    kept = [item for item in items if item.get("project_dir") != str(project_dir)]
    kept.append(record)
    _save_project_index(kept)


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def _active_project_records(cwd: str | os.PathLike[str] | None = None) -> list[dict]:
    current = Path(cwd or os.getcwd()).resolve()
    records = []
    for item in _load_project_index():
        project_dir = Path(item.get("project_dir", "")).expanduser()
        metrics_path = Path(item.get("metrics_path", "")).expanduser()
        if not project_dir or not metrics_path.exists():
            continue
        if _is_relative_to(current, project_dir):
            records.append(item)
    records.sort(key=lambda item: len(item.get("project_dir", "")), reverse=True)
    return records


def add_metric(metric_name: str, metric_description: str, file_path: str = "references/metrics.md"):
    """Backward-compatible global metric append function."""
    path = _resolve_path(file_path)
    result = _append_definition(path, metric_name, metric_description, "global")
    print(f"✅ 成功追加统计口径: {metric_name} 到 {path}")
    return result


def set_metric(metric_name: str, metric_description: str, level: str = "global", project_dir: str | None = None) -> MetricDefinition:
    """Create a global or project-level metric definition."""
    if level not in {"global", "project"}:
        raise ValueError("level must be 'global' or 'project'")

    if level == "global":
        result = _append_definition(GLOBAL_METRICS_PATH, metric_name, metric_description, "global")
        print(f"✅ 成功设置全局统计口径: {metric_name}")
        return result

    project = Path(project_dir or os.getcwd()).resolve()
    metrics_path = project / PROJECT_METRICS_DIRNAME / PROJECT_METRICS_FILENAME
    result = _append_definition(metrics_path, metric_name, metric_description, "project", str(project))
    _record_project(project, metrics_path)
    print(f"✅ 成功设置项目统计口径: {metric_name}")
    print(f"项目目录: {project}")
    return result


def read_effective_metrics(cwd: str | os.PathLike[str] | None = None) -> list[tuple[str, Path, str]]:
    """Return effective metric files for the current directory.

    The result includes the global metrics file first when present, followed by
    active project metrics files whose recorded project directory contains cwd.
    """
    result: list[tuple[str, Path, str]] = []
    if GLOBAL_METRICS_PATH.exists():
        result.append(("global", GLOBAL_METRICS_PATH, ""))
    for item in _active_project_records(cwd):
        result.append(("project", Path(item["metrics_path"]), item["project_dir"]))
    return result


def render_effective_metrics(cwd: str | os.PathLike[str] | None = None) -> str:
    """Render effective metric definitions as a single Markdown document."""
    parts = ["# 当前生效统计口径", ""]
    files = read_effective_metrics(cwd)
    if not files:
        return "# 当前生效统计口径\n\n暂无统计口径定义。\n"
    for level, path, project_dir in files:
        parts.append(f"## {level}: {path}")
        if project_dir:
            parts.append(f"项目目录: `{project_dir}`")
        parts.append("")
        parts.append(path.read_text(encoding="utf-8"))
        parts.append("")
    return "\n".join(parts)


def _parse_metric_blocks(path: Path) -> list[dict]:
    """Parse metric definition blocks from a metrics Markdown file."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE))
    blocks = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append({
            "name": match.group(1).strip(),
            "body": text[start:end].strip(),
            "path": str(path),
        })
    return blocks


def validate_metric_scopes(cwd: str | os.PathLike[str] | None = None) -> list[MetricValidationIssue]:
    """Validate effective metric definitions for enterprise governance."""
    blocks = []
    for _level, path, _project_dir in read_effective_metrics(cwd):
        blocks.extend(_parse_metric_blocks(path))

    issues: list[MetricValidationIssue] = []
    seen: dict[str, list[dict]] = {}
    for block in blocks:
        key = block["name"].strip().lower()
        seen.setdefault(key, []).append(block)
        body = block["body"]
        metric_name = block["name"]
        source_path = block["path"]
        if not body:
            issues.append(MetricValidationIssue(
                "high",
                metric_name,
                source_path,
                "口径定义为空。",
                "补充计算公式、过滤条件、时间范围和适用场景。",
            ))
            continue
        if not re.search(r"\b(sum|count|avg|min|max|distinct|where|group by|=)\b|[+\-*/]", body, re.IGNORECASE):
            issues.append(MetricValidationIssue(
                "medium",
                metric_name,
                source_path,
                "口径缺少可执行或可复核的计算表达。",
                "用 SQL 片段或清晰公式描述指标如何计算。",
            ))
        if not any(token in body for token in ("时间", "日期", "周期", "按天", "按月", "date", "time")):
            issues.append(MetricValidationIssue(
                "low",
                metric_name,
                source_path,
                "口径缺少时间范围或统计周期说明。",
                "说明指标按自然日、业务日、月、季度或指定日期字段统计。",
            ))
        if not any(token in body for token in ("来源", "表", "字段", "source", "table", "column")):
            issues.append(MetricValidationIssue(
                "low",
                metric_name,
                source_path,
                "口径缺少来源表或来源字段说明。",
                "补充来源表、字段、过滤条件和排除规则。",
            ))

    for duplicated in seen.values():
        if len(duplicated) > 1:
            for block in duplicated:
                issues.append(MetricValidationIssue(
                    "high",
                    block["name"],
                    block["path"],
                    "存在同名统计口径定义，可能导致 SQL/报告口径不稳定。",
                    "保留一个权威定义，或明确全局口径与项目口径的覆盖关系。",
                ))
    return issues


def render_metric_validation(issues: list[MetricValidationIssue]) -> str:
    lines = ["# 统计口径校验报告", ""]
    if not issues:
        lines.append("当前生效统计口径未发现明显治理问题。")
        return "\n".join(lines) + "\n"
    lines.append("| 严重级别 | 指标 | 来源 | 问题 | 建议 |")
    lines.append("|---|---|---|---|---|")
    for issue in issues:
        lines.append(
            f"| {issue.severity} | {issue.metric_name} | `{issue.source_path}` | "
            f"{issue.message} | {issue.recommendation} |"
        )
    lines.append("")
    return "\n".join(lines)


def list_metric_files(level: str = "effective", cwd: str | None = None) -> list[tuple[str, Path, str]]:
    if level == "global":
        return [("global", GLOBAL_METRICS_PATH, "")] if GLOBAL_METRICS_PATH.exists() else []
    if level == "project":
        return [
            ("project", Path(item["metrics_path"]), item["project_dir"])
            for item in _load_project_index()
            if item.get("metrics_path") and Path(item["metrics_path"]).exists()
        ]
    if level == "effective":
        return read_effective_metrics(cwd)
    raise ValueError("level must be global, project, or effective")


def _print_metric_files(level: str, cwd: str | None = None) -> None:
    files = list_metric_files(level, cwd)
    if not files:
        print("暂无统计口径定义。")
        return
    for item_level, path, project_dir in files:
        suffix = f" | project={project_dir}" if project_dir else ""
        print(f"{item_level}: {path}{suffix}")


def main():
    parser = argparse.ArgumentParser(description="管理和保存业务数据统计口径")
    subparsers = parser.add_subparsers(dest="command")

    set_parser = subparsers.add_parser("set", help="设置统计口径")
    set_parser.add_argument("--level", choices=["global", "project"], default="global", help="口径级别")
    set_parser.add_argument("--name", "-n", required=True, help="口径名称")
    set_parser.add_argument("--desc", "-d", required=True, help="口径描述和定义")
    set_parser.add_argument("--project-dir", help="项目目录；默认当前执行目录")

    list_parser = subparsers.add_parser("list", help="列出口径文件")
    list_parser.add_argument("--level", choices=["global", "project", "effective"], default="effective")
    list_parser.add_argument("--cwd", help="用于判断项目口径是否生效的当前目录")

    show_parser = subparsers.add_parser("show", help="输出当前生效口径内容")
    show_parser.add_argument("--cwd", help="用于判断项目口径是否生效的当前目录")

    effective_parser = subparsers.add_parser("effective", help="输出当前生效口径内容")
    effective_parser.add_argument("--cwd", help="用于判断项目口径是否生效的当前目录")

    validate_parser = subparsers.add_parser("validate", help="校验当前生效统计口径")
    validate_parser.add_argument("--cwd", help="用于判断项目口径是否生效的当前目录")
    validate_parser.add_argument("--json", action="store_true", help="输出 JSON")

    # Backward-compatible flat options.
    parser.add_argument("--name", "-n", help="口径名称")
    parser.add_argument("--desc", "-d", help="口径描述和定义")
    parser.add_argument("--file", "-f", default="references/metrics.md", help="保存路径")

    args = parser.parse_args()

    if args.command == "set":
        set_metric(args.name, args.desc, args.level, args.project_dir)
    elif args.command == "list":
        _print_metric_files(args.level, args.cwd)
    elif args.command in {"show", "effective"}:
        print(render_effective_metrics(args.cwd))
    elif args.command == "validate":
        issues = validate_metric_scopes(args.cwd)
        if args.json:
            print(json.dumps([issue.__dict__ for issue in issues], ensure_ascii=False, indent=2))
        else:
            print(render_metric_validation(issues))
    elif args.name and args.desc:
        add_metric(args.name, args.desc, args.file)
    else:
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover
    main()
