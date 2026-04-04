# Phase 6: Data Merge Capability - Research

**Researched:** 2026-04-04
**Domain:** Data merging, batch export, SQLite import
**Confidence:** HIGH

## Summary

This phase adds capability to merge multiple SQLite tables into one and export/import as a single file. The implementation leverages existing `DatabaseRepository` for database access, `data_exporter.py` patterns for export, and `data_importer.py` for import. The key feature is a CLI command that allows users to specify multiple source tables and a target table name.

**Primary recommendation:** Create a `DataMerger` class that reads multiple tables using DatabaseRepository, concatenates with pandas, and provides export/import options.

## Phase Requirements

Based on the phase description, this phase should satisfy:

| ID | Description | Research Support |
|----|-------------|-----------------|
| MERGE-01 | Merge multiple SQLite tables into one | pandas concat with DatabaseRepository queries |
| MERGE-02 | Export merged data to CSV/Excel | Reuse data_exporter.py patterns |
| MERGE-03 | Import merged data to SQLite as new table | Reuse data_importer.py patterns |
| MERGE-04 | CLI command for merge operation | argparse subcommand pattern |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.x | Data concatenation | Already used throughout project |
| sqlite3 | stdlib | Database access | Native Python support |
| pydantic | 2.x | Configuration validation | Already used for config validation |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| openpyxl | 3.x | Excel export | For Excel output format |

**Installation:**
No new dependencies required. All libraries already installed.

## Architecture Patterns

### Recommended Project Structure
```
scripts/
├── data_importer.py        # Existing - import from file
├── data_exporter.py        # Existing - export to file
├── data_merger.py          # NEW - merge multiple tables
└── database.py             # Existing - DatabaseRepository

tests/
├── test_data_merger.py     # NEW - merge tests
└── conftest.py             # Existing fixtures
```

### Pattern 1: DataMerger Configuration

```python
# scripts/data_merger.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from pathlib import Path

class MergeConfig(BaseModel):
    """Configuration for table merge operation."""
    source_tables: list[str] = Field(..., min_length=2, description="Tables to merge")
    target_table: str = Field(..., description="Name for merged table")
    db_path: str = Field(default="workspace.db", description="Database path")
    export_file: Optional[str] = Field(default=None, description="Export to file (CSV/Excel)")
    merge_mode: str = Field(default="concat", description="How to merge: concat, union, intersect")

    @field_validator('source_tables')
    @classmethod
    def validate_tables(cls, v: list[str]) -> list[str]:
        if len(set(v)) != len(v):
            raise ValueError("Duplicate table names in source_tables")
        return v
```

### Pattern 2: Merge Operation

```python
# scripts/data_merger.py
import pandas as pd
from database import get_repository
import structlog

logger = structlog.get_logger(__name__)

class DataMerger:
    """Merge multiple SQLite tables into one."""

    def __init__(self, config: MergeConfig):
        self.config = config
        self.repo = get_repository(config.db_path)

    def get_common_columns(self) -> list[str]:
        """Find columns common to all source tables."""
        all_columns = []
        for table in self.config.source_tables:
            with self.repo.connection() as conn:
                df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 0", conn)
                all_columns.append(set(df.columns))

        common = set.intersection(*all_columns)
        return sorted(list(common))

    def merge_tables(self) -> pd.DataFrame:
        """Merge all source tables into one DataFrame."""
        dfs = []

        for table in self.config.source_tables:
            with self.repo.connection() as conn:
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                df['_source_table'] = table
                dfs.append(df)
                logger.info("读取源表", table=table, rows=len(df))

        # Concatenate all DataFrames
        merged = pd.concat(dfs, ignore_index=True)
        logger.info("合并完成", total_rows=len(merged), tables=len(dfs))

        return merged

    def save_to_database(self, df: pd.DataFrame) -> None:
        """Save merged DataFrame to SQLite."""
        with self.repo.connection() as conn:
            df.to_sql(self.config.target_table, conn, index=False, if_exists='replace')
            logger.info("保存到数据库", table=self.config.target_table, rows=len(df))
```

### Pattern 3: CLI Integration

```python
# scripts/data_merger.py - CLI
import argparse
import asyncio

def main():
    parser = argparse.ArgumentParser(description="Merge multiple tables")
    parser.add_argument("--tables", nargs="+", required=True, help="Source tables to merge")
    parser.add_argument("--target", required=True, help="Target table name")
    parser.add_argument("--db", default="workspace.db", help="Database path")
    parser.add_argument("--export", help="Export merged data to file (CSV/Excel)")

    args = parser.parse_args()

    config = MergeConfig(
        source_tables=args.tables,
        target_table=args.target,
        db_path=args.db,
        export_file=args.export
    )

    merger = DataMerger(config)
    merged_df = merger.merge_tables()

    # Save to database
    merger.save_to_database(merged_df)

    # Export if requested
    if args.export:
        if args.export.endswith('.xlsx'):
            merged_df.to_excel(args.export, index=False)
        else:
            merged_df.to_csv(args.export, index=False)
        logger.info("导出完成", file=args.export)

if __name__ == "__main__":
    main()
```

## Common Pitfalls

### Pitfall 1: Column Mismatch

**What goes wrong:** Tables have different columns, concat creates NaN-filled columns.

**Why it happens:** Not all source tables have identical schemas.

**How to avoid:**
- Detect common columns vs all columns
- Log warning when columns differ
- Allow user to choose: common_only or include_all

### Pitfall 2: Memory Issues with Large Tables

**What goes wrong:** Loading all tables into memory causes OOM.

**Why it happens:** Multiple large tables exceed available RAM.

**How to avoid:**
- Use chunked reading for large tables
- Stream to target table instead of building full DataFrame
- Add size warnings before merge

### Pitfall 3: Duplicate Primary Keys

**What goes wrong:** Merged table has duplicate IDs from different source tables.

**Why it happens:** Each source table has its own ID sequence.

**How to avoid:**
- Auto-generate new sequential IDs
- Add source_table column for tracking
- Warn if ID column exists

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | pyproject.toml (existing) |
| Quick run command | `pytest tests/test_data_merger.py -x -v` |
| Full suite command | `pytest tests/ --cov=scripts --cov-report=term-missing` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| MERGE-01 | Merge multiple tables | unit | `pytest tests/test_data_merger.py::TestMergeTables -x` |
| MERGE-02 | Export to CSV/Excel | unit | `pytest tests/test_data_merger.py::TestExport -x` |
| MERGE-03 | Import to SQLite | unit | `pytest tests/test_data_merger.py::TestImport -x` |
| MERGE-04 | CLI command | integration | `pytest tests/test_data_merger.py::TestCLI -x` |

### Sampling Rate
- **Per task commit:** `pytest tests/test_data_merger.py -x -v`
- **Per wave merge:** `pytest tests/ --cov=scripts -v`

### Wave 0 Gaps
- [ ] `scripts/data_merger.py` - DataMerger class
- [ ] `tests/test_data_merger.py` - Merge tests

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already in use
- Architecture: HIGH - Patterns derived from existing codebase
- Pitfalls: MEDIUM - Based on common data merge issues

**Research date:** 2026-04-04
