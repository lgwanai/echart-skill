---
description: "指标变化归因分析"
argument-hint: "<table> <metric> <date_column> <from> <to>"
---

# /echart-why

映射到 echart-skill 原始指令 `/why`。

## 任务

对指标变化做贡献度分解、根因分析和钻取建议。

## 执行规则

1. 使用 echart-skill 的本地优先数据分析流程。
2. 不把大表明细读入模型上下文；使用 DuckDB/Python 在本地计算。
3. 生成报告、Dashboard、图表或导出后，按需要记录审计和血缘。
4. 对图表/Dashboard/Report HTML 运行 `python scripts/validate_chart.py <file>` 质量门。
5. 如需完整流程细节，读取仓库根目录 `SKILL.md` 中对应指令章节。
6. 用户在本命令后的参数作为原始指令参数处理：`$ARGUMENTS`。

## 示例

- `/echart-why orders amount order_date 2024-01 2024-06`
