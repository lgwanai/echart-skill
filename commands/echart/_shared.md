# echart-skill Claude Code Command Index

这些是 Claude Code 可见的 `/echart-*` slash commands。它们映射到 SKILL.md 中的企业 BI 指令，避免和 Claude 内置命令冲突。

| Claude 命令 | 原始指令 | 功能 | 参数 |
|---|---|---|---|
| `/echart-help` | `/help` | 查看 echart-skill 全部命令索引 | `` |
| `/echart-import` | `/import` | 导入 Excel/CSV 数据到本地 DuckDB | `<file> [--table <name>] [--db <path>]` |
| `/echart-query` | `/query` | 执行本地 DuckDB SQL 查询 | `<SQL>` |
| `/echart-chart` | `/chart` | 生成自包含 ECharts 图表 HTML | `<type> <description> [--table <name>] [--output <path>]` |
| `/echart-chart-list` | `/chart-list` | 查看支持的图表类型 | `[category]` |
| `/echart-export` | `/export` | 导出查询或表到 CSV/Excel | `<output> [--table <name>|--query <SQL>]` |
| `/echart-tables` | `/tables` | 查看本地 DuckDB 表和字段结构 | `[table]` |
| `/echart-history` | `/history` | 查看导入历史 | `[--limit <n>]` |
| `/echart-metrics` | `/metrics` | 管理旧版指标定义 | `add|list|show ...` |
| `/echart-scope` | `/scope` | 设置全局/项目级统计口径 | `set|list|show|effective ...` |
| `/echart-privacy` | `/privacy` | 配置隐私脱敏开关 | `mask on|off` |
| `/echart-audit-report` | `/audit-report` | 生成指定日期审计报告 | `--date YYYY-MM-DD [--days 1] [--output <path>]` |
| `/echart-quality` | `/quality` | 生成数据质量评分报告 | `<table> [--db <path>] [--format markdown|json]` |
| `/echart-catalog` | `/catalog` | 生成本地数据资产目录 | `[--db <path>] [--format markdown|json]` |
| `/echart-lineage` | `/lineage` | 记录或查询产物数据血缘 | `record|list ...` |
| `/echart-evidence` | `/evidence` | 生成报告/图表/Dashboard 证据包 | `<artifact> [--lineage-path <path>] [--audit-log <path>]` |
| `/echart-review-report` | `/review-report` | 审阅报告证据和专业性 | `<report> [--format markdown|json]` |
| `/echart-compare` | `/compare` | 执行指标对比分析 | `<table> <metric> <group_column> <baseline> <current>` |
| `/echart-segment` | `/segment` | 执行维度分群分析 | `<table> <dimension> <metric> [--agg sum|avg|count]` |
| `/echart-funnel` | `/funnel` | 执行漏斗转化分析 | `<table> <user_column> <step_column> --steps a,b,c` |
| `/echart-cohort` | `/cohort` | 执行留存/队列分析 | `<table> <user_column> <cohort_date> <activity_date>` |
| `/echart-review-dashboard` | `/review-dashboard` | 审阅 Dashboard 离线性和业务完整性 | `<dashboard.html> [--format markdown|json]` |
| `/echart-whatif` | `/whatif` | 执行 What-if 假设推演 | `<table> <metric> --scenarios name:pct,...` |
| `/echart-contract` | `/contract` | 校验数据契约 | `<table> --columns name:type:required,...` |
| `/echart-brief` | `/brief` | 生成高管摘要 | `<report-or-artifact> [--format markdown|json]` |
| `/echart-pack` | `/pack` | 生成本地 BI 交付包 | `<files...> [--output delivery.zip]` |
| `/echart-clean` | `/clean` | 引导式数据清洗 | `<table> [--config <file>] [--output-table <name>]` |
| `/echart-poll` | `/poll` | 管理轮询数据源 | `status|add|refresh|remove ...` |
| `/echart-dbconn` | `/dbconn` | 管理数据库连接配置 | `add|list|test|import ...` |
| `/echart-schema` | `/schema` | 管理表结构和语义字段定义 | `add|list|show ...` |
| `/echart-dashboard` | `/dashboard` | 生成企业级交互 Dashboard | `<description|config> [--output <path>] [--insights]` |
| `/echart-start` | `/start` | 启动本地预览服务 | `` |
| `/echart-stop` | `/stop` | 停止本地预览服务 | `` |
| `/echart-status` | `/status` | 查看服务和输出状态 | `` |
| `/echart-update` | `/echart-update` | 更新 echart-skill | `` |
| `/echart-analyze` | `/analyze` | 自动分析数据表并发现规律 | `<table> [--dim <columns>]` |
| `/echart-insight` | `/insight` | 针对指定维度生成深度洞察 | `<table> [--dim <column>]` |
| `/echart-report` | `/report` | 生成企业级专家分析报告 | `<table> [--template <name>] [--format markdown|html|json]` |
| `/echart-forecast` | `/forecast` | 执行时间序列预测 | `<table> <date_column> <metric> [--periods <n>]` |
| `/echart-why` | `/why` | 指标变化归因分析 | `<table> <metric> <date_column> <from> <to>` |
| `/echart-context` | `/context` | 会话管理和追问解析 | `start|resolve|history|context|list ...` |

核心原则：本地 DuckDB 计算、明细数据不过大模型、自包含 ECharts 输出、审计与血缘可追踪、专家模式生成企业报告和 Dashboard。
