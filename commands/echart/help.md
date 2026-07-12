---
description: "查看 echart-skill 全部命令索引"
argument-hint: ""
---

# /echart-help

映射到 echart-skill 原始指令 `/help`。

## 任务

列出所有 echart-skill 企业 BI 指令、别名、适用场景和下一步建议。

## 执行规则

1. 使用 echart-skill 的本地优先数据分析流程。
2. 不把大表明细读入模型上下文；使用 DuckDB/Python 在本地计算。
3. 生成报告、Dashboard、图表或导出后，按需要记录审计和血缘。
4. 对图表/Dashboard/Report HTML 运行 `python scripts/validate_chart.py <file>` 质量门。
5. 如需完整流程细节，读取仓库根目录 `SKILL.md` 中对应指令章节。
6. 用户在本命令后的参数作为原始指令参数处理：`$ARGUMENTS`。

## 示例

- `/echart-help`
