"""Validate DuckDB tables against lightweight data contracts."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database import get_repository


@dataclass
class ContractColumn:
    name: str
    data_type: str = ""
    required: bool = False


@dataclass
class ContractIssue:
    severity: str
    category: str
    column: str
    message: str
    recommendation: str


@dataclass
class ContractReport:
    table: str
    generated_at: str
    passed: bool
    issues: list[ContractIssue] = field(default_factory=list)
    actual_columns: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def parse_contract_columns(spec: str) -> list[ContractColumn]:
    columns = []
    for item in spec.split(","):
        item = item.strip()
        if not item:
            continue
        parts = [part.strip() for part in item.split(":")]
        flags = {part.lower() for part in parts[2:]}
        columns.append(ContractColumn(
            name=parts[0],
            data_type=parts[1] if len(parts) > 1 else "",
            required=bool({"required", "notnull", "not_null", "pk"} & flags),
        ))
    return columns


def _compatible_type(expected: str, actual: str) -> bool:
    if not expected:
        return True
    exp = expected.lower().split("(")[0]
    act = actual.lower().split("(")[0]
    aliases = {
        "int": {"integer", "bigint", "smallint", "tinyint", "int"},
        "decimal": {"decimal", "double", "float", "real", "numeric"},
        "varchar": {"varchar", "text", "string"},
        "date": {"date", "timestamp", "datetime"},
    }
    allowed = aliases.get(exp, {exp})
    return act in allowed


def validate_contract(
    table: str,
    expected_columns: list[ContractColumn],
    db_path: str = "workspace.duckdb",
) -> ContractReport:
    repo = get_repository(db_path)
    describe_rows = repo.execute_query_raw(f"DESCRIBE {_quote(table)}")
    actual = {row["column_name"]: str(row["column_type"]) for row in describe_rows}
    issues: list[ContractIssue] = []

    for column in expected_columns:
        if column.name not in actual:
            issues.append(ContractIssue(
                "critical" if column.required else "high",
                "missing_column",
                column.name,
                f"缺少期望字段 `{column.name}`。",
                "补齐字段、修正导入映射，或更新数据契约。",
            ))
            continue
        actual_type = actual[column.name]
        if not _compatible_type(column.data_type, actual_type):
            issues.append(ContractIssue(
                "high",
                "type_mismatch",
                column.name,
                f"字段类型不匹配，期望 `{column.data_type}`，实际 `{actual_type}`。",
                "调整字段类型转换规则，或更新契约中的期望类型。",
            ))
        if column.required:
            null_row = repo.execute_query_raw(
                f"SELECT COUNT(*) AS cnt FROM {_quote(table)} WHERE {_quote(column.name)} IS NULL"
            )[0]
            null_count = int(null_row["cnt"] or 0)
            if null_count > 0:
                issues.append(ContractIssue(
                    "high",
                    "required_nulls",
                    column.name,
                    f"必填字段存在 {null_count} 个空值。",
                    "修复上游数据或在清洗阶段补齐/剔除空值。",
                ))

    return ContractReport(
        table=table,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        passed=not issues,
        issues=issues,
        actual_columns=actual,
    )


def render_contract_markdown(report: ContractReport) -> str:
    lines = [
        "# 数据契约校验报告",
        "",
        f"- 表: `{report.table}`",
        f"- 通过: {report.passed}",
        f"- 生成时间: {report.generated_at}",
        "",
        "## 字段结构",
        "",
        "| 字段 | 实际类型 |",
        "|---|---|",
    ]
    for name, data_type in report.actual_columns.items():
        lines.append(f"| `{name}` | {data_type} |")
    lines.extend(["", "## 问题", ""])
    if not report.issues:
        lines.append("未发现数据契约问题。")
        return "\n".join(lines) + "\n"
    lines.append("| 严重级别 | 类型 | 字段 | 问题 | 建议 |")
    lines.append("|---|---|---|---|---|")
    for issue in report.issues:
        lines.append(f"| {issue.severity} | {issue.category} | `{issue.column}` | {issue.message} | {issue.recommendation} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="校验 DuckDB 表是否符合数据契约")
    parser.add_argument("table")
    parser.add_argument("--columns", required=True, help="字段契约，例如 order_id:VARCHAR:required,amount:DECIMAL")
    parser.add_argument("--db", default="workspace.duckdb")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    report = validate_contract(args.table, parse_contract_columns(args.columns), args.db)
    if args.format == "json":
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_contract_markdown(report))


if __name__ == "__main__":  # pragma: no cover
    main()
