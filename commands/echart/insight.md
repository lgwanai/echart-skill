---
description: "针对指定维度生成深度洞察"
argument-hint: "<table> [--dim <column>]"
---

# /echart-insight

映射到 echart-skill 原始指令 `/insight`。

## 任务

围绕指定维度/指标做更聚焦的洞察分析。

## 执行规则

1. 使用 echart-skill 的本地优先数据分析流程。
2. 不把大表明细读入模型上下文；使用 DuckDB/Python 在本地计算。
3. 生成报告、Dashboard、图表或导出后，按需要记录审计和血缘。
4. 对图表/Dashboard/Report HTML 运行 `python scripts/validate_chart.py <file>` 质量门。
5. 如需完整流程细节，读取仓库根目录 `SKILL.md` 中对应指令章节。
6. 用户在本命令后的参数作为原始指令参数处理：`$ARGUMENTS`。

## 示例

- `/echart-insight sales --dim region`
