---
description: "导入 Excel/CSV 数据到本地 DuckDB"
argument-hint: "<file> [--table <name>] [--db <path>]"
---

# /echart-import

映射到 echart-skill 原始指令 `/import`。

## 任务

导入文件，处理表头、合并单元格、表名标准化，并记录导入元数据。

## 执行规则

1. 使用 echart-skill 的本地优先数据分析流程。
2. 不把大表明细读入模型上下文；使用 DuckDB/Python 在本地计算。
3. 生成报告、Dashboard、图表或导出后，按需要记录审计和血缘。
4. 对图表/Dashboard/Report HTML 运行 `python scripts/validate_chart.py <file>` 质量门。
5. 如需完整流程细节，读取仓库根目录 `SKILL.md` 中对应指令章节。
6. 用户在本命令后的参数作为原始指令参数处理：`$ARGUMENTS`。

## 示例

- `/echart-import data.xlsx`
- `/echart-import sales.csv --table sales`
