---
description: "执行漏斗转化分析"
argument-hint: "<table> <user_column> <step_column> --steps a,b,c"
---

# /echart-funnel

映射到 echart-skill 原始指令 `/funnel`。

## 任务

按指定步骤顺序计算去重用户数、首步转化率、上步转化率和流失人数。

## 执行规则

1. 使用 echart-skill 的本地优先数据分析流程。
2. 不把大表明细读入模型上下文；使用 DuckDB/Python 在本地计算。
3. 生成报告、Dashboard、图表或导出后，按需要记录审计和血缘。
4. 对图表/Dashboard/Report HTML 运行 `python scripts/validate_chart.py <file>` 质量门。
5. 如需完整流程细节，读取仓库根目录 `SKILL.md` 中对应指令章节。
6. 用户在本命令后的参数作为原始指令参数处理：`$ARGUMENTS`。

## 示例

- `/echart-funnel events user_id step --steps visit,signup,pay`
