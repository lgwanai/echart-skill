---
description: "执行留存/队列分析"
argument-hint: "<table> <user_column> <cohort_date> <activity_date>"
---

# /echart-cohort

映射到 echart-skill 原始指令 `/cohort`。

## 任务

按天/周/月队列计算用户留存矩阵，支撑增长、复购和活跃质量分析。

## 执行规则

1. 使用 echart-skill 的本地优先数据分析流程。
2. 不把大表明细读入模型上下文；使用 DuckDB/Python 在本地计算。
3. 生成报告、Dashboard、图表或导出后，按需要记录审计和血缘。
4. 对图表/Dashboard/Report HTML 运行 `python scripts/validate_chart.py <file>` 质量门。
5. 如需完整流程细节，读取仓库根目录 `SKILL.md` 中对应指令章节。
6. 用户在本命令后的参数作为原始指令参数处理：`$ARGUMENTS`。

## 示例

- `/echart-cohort activity user_id signup_date active_date --unit month`
