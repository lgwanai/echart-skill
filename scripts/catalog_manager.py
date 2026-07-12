"""Local data catalog for DuckDB-backed BI assets."""

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
from scripts.data_quality import analyze_table_quality


@dataclass
class CatalogColumn:
    name: str
    data_type: str
    nullable: bool = True
    null_pct: float = 0.0
    unique_pct: float = 0.0
    role: str = "unknown"


@dataclass
class CatalogTable:
    name: str
    row_count: int
    column_count: int
    quality_score: int
    quality_grade: str
    columns: list[CatalogColumn] = field(default_factory=list)


@dataclass
class DataCatalog:
    db_path: str
    generated_at: str
    tables: list[CatalogTable] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _infer_role(name: str, data_type: str, unique_pct: float) -> str:
    lower = name.lower()
    dtype = data_type.lower()
    if lower.endswith("_id") or lower == "id":
        return "identifier"
    if "date" in lower or "time" in lower or "date" in dtype or "time" in dtype:
        return "time"
    if any(token in dtype for token in ("int", "decimal", "double", "float", "numeric")):
        return "measure"
    if unique_pct >= 95:
        return "identifier"
    return "dimension"


def list_duckdb_tables(db_path: str = "workspace.duckdb") -> list[str]:
    repo = get_repository(db_path)
    rows = repo.execute_query_raw(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'main' AND table_type = 'BASE TABLE' ORDER BY table_name"
    )
    return [row["table_name"] for row in rows]


def build_catalog(db_path: str = "workspace.duckdb", include_quality: bool = True) -> DataCatalog:
    repo = get_repository(db_path)
    tables: list[CatalogTable] = []

    for table in list_duckdb_tables(db_path):
        row_count = int(repo.execute_query_raw(f"SELECT COUNT(*) AS cnt FROM {_quote(table)}")[0]["cnt"])
        describe_rows = repo.execute_query_raw(f"DESCRIBE {_quote(table)}")
        quality = analyze_table_quality(table, db_path) if include_quality else None
        quality_columns = quality.metrics.get("columns", {}) if quality else {}

        columns: list[CatalogColumn] = []
        for row in describe_rows:
            name = row["column_name"]
            stats = quality_columns.get(name, {})
            unique_pct = float(stats.get("unique_pct", 0.0))
            data_type = str(row["column_type"])
            columns.append(CatalogColumn(
                name=name,
                data_type=data_type,
                nullable=str(row.get("null", "YES")).upper() != "NO",
                null_pct=float(stats.get("null_pct", 0.0)),
                unique_pct=unique_pct,
                role=_infer_role(name, data_type, unique_pct),
            ))

        tables.append(CatalogTable(
            name=table,
            row_count=row_count,
            column_count=len(columns),
            quality_score=quality.score if quality else 0,
            quality_grade=quality.grade if quality else "",
            columns=columns,
        ))

    return DataCatalog(
        db_path=str(Path(db_path).resolve()) if db_path != ":memory:" else db_path,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        tables=tables,
    )


def render_catalog_markdown(catalog: DataCatalog) -> str:
    lines = [
        "# 数据资产目录",
        "",
        f"- 数据库: `{catalog.db_path}`",
        f"- 生成时间: {catalog.generated_at}",
        f"- 表数量: {len(catalog.tables)}",
        "",
    ]
    if not catalog.tables:
        lines.append("暂无数据表。")
        return "\n".join(lines) + "\n"

    lines.extend(["## 表概览", "", "| 表 | 行数 | 字段数 | 质量分 | 等级 |", "|---|---:|---:|---:|---|"])
    for table in catalog.tables:
        lines.append(f"| `{table.name}` | {table.row_count} | {table.column_count} | {table.quality_score} | {table.quality_grade} |")

    for table in catalog.tables:
        lines.extend(["", f"## {table.name}", "", "| 字段 | 类型 | 角色 | 缺失率 | 唯一率 |", "|---|---|---|---:|---:|"])
        for column in table.columns:
            lines.append(
                f"| `{column.name}` | {column.data_type} | {column.role} | "
                f"{column.null_pct:.2f}% | {column.unique_pct:.2f}% |"
            )
    lines.append("")
    return "\n".join(lines)


def write_catalog(catalog: DataCatalog, output_path: str = "", output_format: str = "markdown") -> Path:
    if output_path:
        path = Path(output_path)
    else:
        out_dir = PROJECT_ROOT / "outputs" / "catalog"
        out_dir.mkdir(parents=True, exist_ok=True)
        suffix = "json" if output_format == "json" else "md"
        path = out_dir / f"data_catalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{suffix}"
    path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        path.write_text(json.dumps(catalog.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        path.write_text(render_catalog_markdown(catalog), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="生成本地 DuckDB 数据资产目录")
    parser.add_argument("--db", default="workspace.duckdb", help="DuckDB 数据库路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", help="输出路径")
    parser.add_argument("--no-quality", action="store_true", help="跳过数据质量评分")
    parser.add_argument("--print", action="store_true", help="同时打印目录")
    args = parser.parse_args()

    catalog = build_catalog(args.db, include_quality=not args.no_quality)
    path = write_catalog(catalog, args.output or "", args.format)
    if args.print:
        if args.format == "json":
            print(json.dumps(catalog.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(render_catalog_markdown(catalog))
    print(f"✅ 数据资产目录已生成: {path}")


if __name__ == "__main__":  # pragma: no cover
    main()
