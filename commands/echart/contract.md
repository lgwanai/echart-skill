---
description: "校验数据契约"
argument-hint: "<table> --columns name:type:required,..."
---

# /echart-contract

映射到 echart-skill 原始指令 `/contract`。

## 任务

将真实 DuckDB 表结构与期望字段、类型、必填约束进行比对，发现上游结构漂移。

## 执行规则

1. 使用 echart-skill 的本地优先数据分析流程。
2. 不把大表明细读入模型上下文；使用 DuckDB/Python 在本地计算。
3. 生成报告、Dashboard、图表或导出后，按需要记录审计和血缘。
4. 对图表/Dashboard/Report HTML 运行 `python scripts/validate_chart.py <file>` 质量门。
5. 如需完整流程细节，读取仓库根目录 `SKILL.md` 中对应指令章节。
6. 用户在本命令后的参数作为原始指令参数处理：`$ARGUMENTS`。

## 示例

- `/echart-contract orders --columns order_id:VARCHAR:required,amount:DECIMAL`
