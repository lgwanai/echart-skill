---
description: "生成自包含 ECharts 图表 HTML"
argument-hint: "<type> <description> [--table <name>] [--output <path>]"
---

# /echart-chart

映射到 echart-skill 原始指令 `/chart`。

## 任务

按配方模式读取 references/examples，查询真实数据，内联本地 ECharts，并运行 validate_chart.py。

## 执行规则

1. 使用 echart-skill 的本地优先数据分析流程。
2. 不把大表明细读入模型上下文；使用维护好的本地脚本执行计算和查询。
3. 生成报告、Dashboard、图表或导出后，按需要记录审计和血缘。
4. 自然语言分析请求也适用统一 SQL 规则；不得因为用户没有显式使用 `/echart-query` 就手写数据库连接代码。
5. 对图表/Dashboard/Report HTML 运行 `python scripts/validate_chart.py <file>` 质量门。
6. 如需完整流程细节，读取仓库根目录 `SKILL.md` 中对应指令章节。
7. 用户在本命令后的参数作为原始指令参数处理：`$ARGUMENTS`。

8. [MANDATORY] 所有数据库查询和取数动作，包括自然语言分析、结构探索、聚合、同比/环比、分维度分析、报告取数、图表取数和 Dashboard 取数，都必须生成 SQL 并使用 `scripts/sql_runner.py`、`scripts/db_cli.py` 或 `scripts/db_manager.py` 执行；`scripts/analysis_runner.py` 仅是简单聚合的可选快捷方式。
9. [FAIL] 禁止在任何指令中使用 `python3 << 'PYEOF'` / `python << 'PY'` heredoc、`psycopg2.connect(...)`、`psycopg.connect(...)`、`pymysql.connect(...)`、`duckdb.connect(...)`、`create_engine(...)`、`.cursor()`、`cur.execute(...)` 或临时 Python 代码直接连接数据库/执行 SQL。
10. 执行前必须读取 schema 和当前生效统计口径：`python scripts/metrics_manager.py effective`。如果口径中维护了业务集合（如商圈酒店集合），SQL 必须使用该集合，例如 `hotel_name IN (...)`；不得把商圈误当作不存在的字段，也不得自行用关键词 LIKE 猜集合。
11. PostgreSQL/MySQL 查询使用 `python scripts/sql_runner.py --profile <name> --sql "<SELECT ...>" --output json` 或 `python scripts/sql_runner.py --profile <name> --file queries/<task>.sql --output json`；未配置 profile 时，使用 `python scripts/sql_runner.py --type postgresql --host <host> --database <db> --username <user> --password-env DB_PASSWORD --sql "<SELECT ...>" --output json`。可以写 SQL 文件；不得把密码写入命令或临时代码。
12. Agent 可以写 SQL 和 SQL 文件，禁止写的是临时数据库连接代码；不要为了查数写 Python，也不要为了避免 SQL 而堆很多参数。
13. 任何输出形态都必须满足企业 BI 交付标准：查询/导出要有 `.meta.json` 旁路元数据和血缘，报告/图表/Dashboard 要有统计口径说明、数据血缘/来源、生成时间、证据引用、限制说明和专业版式。
14. 每个图表区域必须有 `查看数据` 按钮和对应的默认隐藏数据表，点击后可查看该图实际数据；每个图表卡片/面板必须写清图表级统计口径、数据来源/query hash。
15. 返回结果前，如过程输出包含上述违规模式，必须运行 `python scripts/validate_agent_output.py <log-or-text>` 并修复为 sql_runner/db_cli 流程；对生成文件运行 `python scripts/validate_output_quality.py <artifact>`，HTML 图表/Dashboard/Report 还必须运行 `python scripts/validate_chart.py <artifact>`。
13. HTML 图表/Dashboard/Report 必须是自包含单文件：禁止 CDN、禁止 `<script src="https://...">`，必须内联本地 `assets/echarts/echarts.min.js`。
14. Dashboard 必须使用 `dashboard-container`、`dashboard-header`、`kpi-card`、`dashboard-grid`、`chart-card`、`chart-surface` 等企业 BI 结构。
15. 禁止 `.row` / `.full` 伪全宽网格；大图必须把 `chart-card--wide` / `full-width` / `grid-column: 1 / -1` 加在实际 chart card 上。
16. 多图 Dashboard 的第一张核心分析卡必须 wide/full；两列 Dashboard 禁止出现 5/7 个普通半宽 `chart-card` 造成孤儿行和大面积空白，必须提升一个核心卡为 wide/full 或补齐配对。
17. 数据必须用 Python `json.dumps(..., ensure_ascii=False, default=str)` 序列化后写入 HTML；禁止手写大型 JS 对象和字符串拼接 KPI HTML。
18. 每个图表卡片必须有 `查看数据` 按钮、默认隐藏数据表、统计口径和数据来源；按钮要能打开对应表格。
19. `python scripts/validate_chart.py <output.html>` 或 `python scripts/validate_output_quality.py <output.html>` 返回非 0 时，必须修复后重跑，绝不能把文件路径返回给用户。

## 示例

- `/echart-chart bar 销售额按地区 --table sales`
