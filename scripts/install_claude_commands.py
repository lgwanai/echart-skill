"""Install Claude Code slash commands for echart-skill.

Claude Code does not automatically expose command rows in SKILL.md as slash
commands. This installer creates lightweight `/echart-*` command wrappers under
`~/.claude/commands` and keeps the source command docs in this repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "commands" / "echart"
CLAUDE_COMMANDS_DIR = Path.home() / ".claude" / "commands"


@dataclass(frozen=True)
class CommandSpec:
    name: str
    original: str
    description: str
    argument_hint: str
    detail: str
    examples: tuple[str, ...]


COMMANDS: tuple[CommandSpec, ...] = (
    CommandSpec("help", "/help", "查看 echart-skill 全部命令索引", "", "列出所有 echart-skill 企业 BI 指令、别名、适用场景和下一步建议。", ("/echart-help",)),
    CommandSpec("import", "/import", "导入 Excel/CSV 数据到本地 DuckDB", "<file> [--table <name>] [--db <path>]", "导入文件，处理表头、合并单元格、表名标准化，并记录导入元数据。", ("/echart-import data.xlsx", "/echart-import sales.csv --table sales")),
    CommandSpec("query", "/query", "通过统一 SQL runner 执行 DuckDB/PostgreSQL/MySQL 查询", "<SQL>", "根据 schema 与当前生效统计口径生成 SQL，并使用 scripts/sql_runner.py 执行；可以用 --sql 直接传 SQL，也可以用 --file 执行 SQL 文件。禁止临时 Python 连接数据库。不要把大表明细读入模型上下文，只返回必要聚合、样例或输出文件路径。", ("/echart-query SELECT * FROM sales LIMIT 10", "python scripts/metrics_manager.py effective", "python scripts/sql_runner.py --profile analytics --sql \"SELECT region, SUM(amount) AS total FROM sales GROUP BY region\" --output json", "python scripts/sql_runner.py --profile analytics --file queries/monthly_sales.sql --output json")),
    CommandSpec("analysis-query", "/analysis-query", "可选快捷聚合查询", "entity-search|period-compare|segment|trend|topn ...", "可选使用 scripts/analysis_runner.py 执行简单实体搜索、区间对比、分维度聚合、趋势和 TopN 查询。复杂业务问题不要强行堆参数；应读取 schema 与当前生效统计口径，生成 SQL 后交给 scripts/sql_runner.py 执行。", ("python scripts/metrics_manager.py effective", "python scripts/sql_runner.py --profile analytics --file queries/hotel_business_scope_analysis.sql --output json", "python scripts/analysis_runner.py period-compare --profile analytics --table orders --date-column order_date --metric amount --dimension city --baseline-start 2025-01-01 --baseline-end 2025-06-30 --current-start 2026-01-01 --current-end 2026-06-30 --output json",)),
    CommandSpec("chart", "/chart", "生成自包含 ECharts 图表 HTML", "<type> <description> [--table <name>] [--output <path>]", "按配方模式读取 references/examples，查询真实数据，内联本地 ECharts，并运行 validate_chart.py。", ("/echart-chart bar 销售额按地区 --table sales",)),
    CommandSpec("chart-list", "/chart-list", "查看支持的图表类型", "[category]", "展示基础、统计、层级、关系、地理、3D、专业图表等支持范围。", ("/echart-chart-list", "/echart-chart-list 3d")),
    CommandSpec("export", "/export", "导出查询或表到 CSV/Excel", "<output> [--table <name>|--query <SQL>]", "从 DuckDB 导出本地文件，保留数据本地化与审计链路。", ("/echart-export result.csv --table sales",)),
    CommandSpec("tables", "/tables", "查看本地 DuckDB 表和字段结构", "[table]", "列出表、字段类型、样例和可分析字段，供后续查询/报告/看板使用。", ("/echart-tables", "/echart-tables sales")),
    CommandSpec("history", "/history", "查看导入历史", "[--limit <n>]", "读取导入元数据，展示文件来源、表名、导入时间和使用记录。", ("/echart-history --limit 20",)),
    CommandSpec("metrics", "/metrics", "管理旧版指标定义", "add|list|show ...", "兼容旧指标管理入口；新统计口径优先使用 /echart-scope。", ("/echart-metrics list",)),
    CommandSpec("scope", "/scope", "设置全局/项目级统计口径", "set|list|show|effective ...", "设置企业指标口径。项目级口径记录项目目录，只在该目录及子目录下生效。", ("/echart-scope set --level project --name GMV --desc \"SUM(pay_amount)\"", "/echart-scope show")),
    CommandSpec("privacy", "/privacy", "配置隐私脱敏开关", "mask on|off", "PII 脱敏默认关闭；开启后对手机号、邮箱、身份证、银行卡、薪资、地址等字段脱敏。", ("/echart-privacy mask on", "/echart-privacy mask off")),
    CommandSpec("audit-report", "/audit-report", "生成指定日期审计报告", "--date YYYY-MM-DD [--days 1] [--output <path>]", "汇总用户指令、查询表、访问列、行数、脱敏状态、分类级别、变更标记和 query hash。", ("/echart-audit-report --date 2026-06-29",)),
    CommandSpec("quality", "/quality", "生成数据质量评分报告", "<table> [--db <path>] [--format markdown|json]", "检查缺失率、重复行、常量列、疑似 ID 字段，输出质量分、等级和分析限制。", ("/echart-quality orders --format markdown",)),
    CommandSpec("catalog", "/catalog", "生成本地数据资产目录", "[--db <path>] [--format markdown|json]", "扫描 DuckDB 表、字段、字段角色、缺失率、唯一率和质量评分，形成企业数据资产目录。", ("/echart-catalog --db workspace.duckdb --format markdown",)),
    CommandSpec("lineage", "/lineage", "记录或查询产物数据血缘", "record|list ...", "记录报告、Dashboard、图表、导出文件的来源表、字段、统计口径和 query hash。", ("/echart-lineage list --table orders",)),
    CommandSpec("evidence", "/evidence", "生成报告/图表/Dashboard 证据包", "<artifact> [--lineage-path <path>] [--audit-log <path>]", "汇总产物 SHA256、血缘、审计匹配记录和生效统计口径，支持结论复核。", ("/echart-evidence outputs/reports/sales.md",)),
    CommandSpec("review-report", "/review-report", "审阅报告证据和专业性", "<report> [--format markdown|json]", "检查报告是否具备数字证据、结构、图表/附录、行动建议、口径限制说明和专业表达。", ("/echart-review-report outputs/reports/sales.md",)),
    CommandSpec("compare", "/compare", "执行指标对比分析", "<table> <metric> <group_column> <baseline> <current>", "对指定基准组和对比组进行本地 SUM/AVG/COUNT 指标变化分析，输出变化量和变化率。", ("/echart-compare sales amount month 2024-01 2024-02",)),
    CommandSpec("segment", "/segment", "执行维度分群分析", "<table> <dimension> <metric> [--agg sum|avg|count]", "按业务维度聚合指标，输出分群规模、指标值和占比，用于结构分析和重点客群识别。", ("/echart-segment sales region amount --agg sum",)),
    CommandSpec("funnel", "/funnel", "执行漏斗转化分析", "<table> <user_column> <step_column> --steps a,b,c", "按指定步骤顺序计算去重用户数、首步转化率、上步转化率和流失人数。", ("/echart-funnel events user_id step --steps visit,signup,pay",)),
    CommandSpec("cohort", "/cohort", "执行留存/队列分析", "<table> <user_column> <cohort_date> <activity_date>", "按天/周/月队列计算用户留存矩阵，支撑增长、复购和活跃质量分析。", ("/echart-cohort activity user_id signup_date active_date --unit month",)),
    CommandSpec("review-dashboard", "/review-dashboard", "审阅 Dashboard 离线性和业务完整性", "<dashboard.html> [--format markdown|json]", "检查 Dashboard 是否存在外部网络资源、ECharts 初始化、稳定容器、KPI 总览、洞察和标题。", ("/echart-review-dashboard outputs/dashboards/sales.html",)),
    CommandSpec("whatif", "/whatif", "执行 What-if 假设推演", "<table> <metric> --scenarios name:pct,...", "基于本地指标基准值推演不同增长/下降场景，输出推演值和变化量。", ("/echart-whatif sales amount --scenarios conservative:-5,base:0,growth:10",)),
    CommandSpec("contract", "/contract", "校验数据契约", "<table> --columns name:type:required,...", "将真实 DuckDB 表结构与期望字段、类型、必填约束进行比对，发现上游结构漂移。", ("/echart-contract orders --columns order_id:VARCHAR:required,amount:DECIMAL",)),
    CommandSpec("brief", "/brief", "生成高管摘要", "<report-or-artifact> [--format markdown|json]", "从报告或分析产物中提取关键数字、主要结论、行动建议和口径限制。", ("/echart-brief outputs/reports/sales.md",)),
    CommandSpec("pack", "/pack", "生成本地 BI 交付包", "<files...> [--output delivery.zip]", "把报告、Dashboard、证据包、审计摘要等文件打包为带 manifest 和 SHA256 的本地 ZIP。", ("/echart-pack outputs/reports/sales.md outputs/evidence/sales.md --output delivery.zip",)),
    CommandSpec("clean", "/clean", "引导式数据清洗", "<table> [--config <file>] [--output-table <name>]", "按 data_cleaning_workflow 诊断字段、缺失、重复、异常，再执行非破坏式清洗。", ("/echart-clean orders --output-table orders_cleaned",)),
    CommandSpec("poll", "/poll", "管理轮询数据源", "status|add|refresh|remove ...", "管理 HTTP/数据库轮询任务，自动刷新本地 DuckDB 表。", ("/echart-poll status",)),
    CommandSpec("dbconn", "/dbconn", "管理数据库连接配置", "add|list|test|import ...", "管理 MySQL/PostgreSQL/MongoDB 连接，支持全局/项目级连接配置；PostgreSQL/MySQL 查询必须走 scripts/sql_runner.py。", ("/echart-dbconn list", "python scripts/sql_runner.py --profile analytics --sql \"SELECT 1\" --output json")),
    CommandSpec("schema", "/schema", "管理表结构和语义字段定义", "add|list|show ...", "维护表结构、字段角色、主键、关联和业务说明，供专家分析和 SQL 生成使用。", ("/echart-schema show orders",)),
    CommandSpec("dashboard", "/dashboard", "生成企业级交互 Dashboard", "<description|config> [--output <path>] [--insights]", "按 Dashboard 工作流和专家库生成 KPI、趋势、排行、结构、异常、地理等模块，并通过运行时质量门。", ("/echart-dashboard 创建销售经营分析仪表盘 --insights",)),
    CommandSpec("start", "/start", "启动本地预览服务", "", "按配置启动本地 HTTP 服务，仅用于预览自包含 HTML 输出。", ("/echart-start",)),
    CommandSpec("stop", "/stop", "停止本地预览服务", "", "停止 echart-skill 本地预览服务。", ("/echart-stop",)),
    CommandSpec("status", "/status", "查看服务和输出状态", "", "查看本地服务状态、端口、可访问图表和输出文件。", ("/echart-status",)),
    CommandSpec("update", "/echart-update", "更新 echart-skill", "", "从远端更新 skill，并在修改前备份旧文件。", ("/echart-update",)),
    CommandSpec("analyze", "/analyze", "自动分析数据表并发现规律", "<table> [--dim <columns>]", "运行数据画像、排名、构成、趋势、异常、相关性等洞察发现，输出置信度和限制。", ("/echart-analyze sales",)),
    CommandSpec("insight", "/insight", "针对指定维度生成深度洞察", "<table> [--dim <column>]", "围绕指定维度/指标做更聚焦的洞察分析。", ("/echart-insight sales --dim region",)),
    CommandSpec("report", "/report", "生成企业级专家分析报告", "<table> [--template <name>] [--format markdown|html|json]", "按专家库和金字塔结构生成结论先行、图表举证、归因解释、行动建议和附录数据的报告。", ("/echart-report sales --template sales --format html",)),
    CommandSpec("forecast", "/forecast", "执行时间序列预测", "<table> <date_column> <metric> [--periods <n>]", "使用本地预测方法输出趋势预测和置信说明，零外部依赖。", ("/echart-forecast orders order_date amount --periods 6",)),
    CommandSpec("why", "/why", "指标变化归因分析", "<table> <metric> <date_column> <from> <to>", "对指标变化做贡献度分解、根因分析和钻取建议。", ("/echart-why orders amount order_date 2024-01 2024-06",)),
    CommandSpec("context", "/context", "会话管理和追问解析", "start|resolve|history|context|list ...", "维护当前分析表、指标、维度、时间范围和追问链。", ("/echart-context start sales", "/echart-context resolve \"上个月呢？\"")),
)


def _frontmatter(description: str, argument_hint: str) -> str:
    return f"---\ndescription: \"{description}\"\nargument-hint: \"{argument_hint}\"\n---\n"


def _command_source(spec: CommandSpec) -> str:
    examples = "\n".join(f"- `{example}`" for example in spec.examples)
    sql_guard = (
        "8. [MANDATORY] 所有数据库查询和取数动作，包括自然语言分析、结构探索、聚合、同比/环比、分维度分析、报告取数、图表取数和 Dashboard 取数，"
        "都必须生成 SQL 并使用 `scripts/sql_runner.py`、`scripts/db_cli.py` 或 `scripts/db_manager.py` 执行；`scripts/analysis_runner.py` 仅是简单聚合的可选快捷方式。\n"
        "9. [FAIL] 禁止在任何指令中使用 `python3 << 'PYEOF'` / `python << 'PY'` heredoc、"
        "`psycopg2.connect(...)`、`psycopg.connect(...)`、`pymysql.connect(...)`、`duckdb.connect(...)`、"
        "`create_engine(...)`、`.cursor()`、`cur.execute(...)` 或临时 Python 代码直接连接数据库/执行 SQL。\n"
        "10. 执行前必须读取 schema 和当前生效统计口径：`python scripts/metrics_manager.py effective`。如果口径中维护了业务集合（如商圈酒店集合），SQL 必须使用该集合，例如 `hotel_name IN (...)`；不得把商圈误当作不存在的字段，也不得自行用关键词 LIKE 猜集合。\n"
        "11. PostgreSQL/MySQL 查询使用 `python scripts/sql_runner.py --profile <name> --sql \"<SELECT ...>\" --output json` 或 `python scripts/sql_runner.py --profile <name> --file queries/<task>.sql --output json`；"
        "未配置 profile 时，使用 `python scripts/sql_runner.py --type postgresql --host <host> --database <db> --username <user> --password-env DB_PASSWORD --sql \"<SELECT ...>\" --output json`。"
        "可以写 SQL 文件；不得把密码写入命令或临时代码。\n"
        "12. Agent 可以写 SQL 和 SQL 文件，禁止写的是临时数据库连接代码；不要为了查数写 Python，也不要为了避免 SQL 而堆很多参数。\n"
        "13. 任何输出形态都必须满足企业 BI 交付标准：查询/导出要有 `.meta.json` 旁路元数据和血缘，报告/图表/Dashboard 要有统计口径说明、数据血缘/来源、生成时间、证据引用、限制说明和专业版式。\n"
        "14. 每个图表区域必须有 `查看数据` 按钮和对应的默认隐藏数据表，点击后可查看该图实际数据；每个图表卡片/面板必须写清图表级统计口径、数据来源/query hash。\n"
        "15. 返回结果前，如过程输出包含上述违规模式，必须运行 `python scripts/validate_agent_output.py <log-or-text>` 并修复为 sql_runner/db_cli 流程；对生成文件运行 `python scripts/validate_output_quality.py <artifact>`，HTML 图表/Dashboard/Report 还必须运行 `python scripts/validate_chart.py <artifact>`。\n"
    )
    html_guard = ""
    if spec.name in {"chart", "dashboard", "report", "review-dashboard"}:
        html_guard = (
            "13. HTML 图表/Dashboard/Report 必须是自包含单文件：禁止 CDN、禁止 `<script src=\"https://...\">`，必须内联本地 `assets/echarts/echarts.min.js`。\n"
            "14. Dashboard 必须使用 `dashboard-container`、`dashboard-header`、`kpi-card`、`dashboard-grid`、`chart-card`、`chart-surface` 等企业 BI 结构。\n"
            "15. 禁止 `.row` / `.full` 伪全宽网格；大图必须把 `chart-card--wide` / `full-width` / `grid-column: 1 / -1` 加在实际 chart card 上。\n"
            "16. 多图 Dashboard 的第一张核心分析卡必须 wide/full；两列 Dashboard 禁止出现 5/7 个普通半宽 `chart-card` 造成孤儿行和大面积空白，必须提升一个核心卡为 wide/full 或补齐配对。\n"
            "17. 数据必须用 Python `json.dumps(..., ensure_ascii=False, default=str)` 序列化后写入 HTML；禁止手写大型 JS 对象和字符串拼接 KPI HTML。\n"
            "18. 每个图表卡片必须有 `查看数据` 按钮、默认隐藏数据表、统计口径和数据来源；按钮要能打开对应表格。\n"
            "19. `python scripts/validate_chart.py <output.html>` 或 `python scripts/validate_output_quality.py <output.html>` 返回非 0 时，必须修复后重跑，绝不能把文件路径返回给用户。\n"
        )
    return (
        _frontmatter(spec.description, spec.argument_hint)
        + f"\n# /echart-{spec.name}\n\n"
        + f"映射到 echart-skill 原始指令 `{spec.original}`。\n\n"
        + f"## 任务\n\n{spec.detail}\n\n"
        + "## 执行规则\n\n"
        + "1. 使用 echart-skill 的本地优先数据分析流程。\n"
        + "2. 不把大表明细读入模型上下文；使用维护好的本地脚本执行计算和查询。\n"
        + "3. 生成报告、Dashboard、图表或导出后，按需要记录审计和血缘。\n"
        + "4. 自然语言分析请求也适用统一 SQL 规则；不得因为用户没有显式使用 `/echart-query` 就手写数据库连接代码。\n"
        + "5. 对图表/Dashboard/Report HTML 运行 `python scripts/validate_chart.py <file>` 质量门。\n"
        + "6. 如需完整流程细节，读取仓库根目录 `SKILL.md` 中对应指令章节。\n"
        + "7. 用户在本命令后的参数作为原始指令参数处理：`$ARGUMENTS`。\n\n"
        + sql_guard
        + html_guard
        + ("\n" if sql_guard or html_guard else "")
        + "## 示例\n\n"
        + examples
        + "\n"
    )


def _shared_source() -> str:
    rows = "\n".join(
        f"| `/echart-{spec.name}` | `{spec.original}` | {spec.description} | `{spec.argument_hint}` |"
        for spec in COMMANDS
    )
    return (
        "# echart-skill Claude Code Command Index\n\n"
        "这些是 Claude Code 可见的 `/echart-*` slash commands。它们映射到 SKILL.md 中的企业 BI 指令，避免和 Claude 内置命令冲突。\n\n"
        "| Claude 命令 | 原始指令 | 功能 | 参数 |\n"
        "|---|---|---|---|\n"
        + rows
        + "\n\n"
        "核心原则：Agent 可以根据 schema 和当前生效统计口径生成 SQL，也可以写 SQL 文件，但必须通过 `scripts/sql_runner.py --sql` / `scripts/sql_runner.py --file` / `scripts/db_cli.py` / `scripts/db_manager.py` 执行，`scripts/analysis_runner.py` 只作为简单聚合快捷方式；不得用临时 heredoc Python 连接数据库，不得从 `conn = ...` 开始写查数脚本。执行前读取 `python scripts/metrics_manager.py effective`，业务集合口径（如商圈酒店集合）必须按口径展开为 SQL 条件，例如 `hotel_name IN (...)`，不能假设存在商圈字段，也不能自行用关键词 LIKE 猜集合。分析代码仅用于 SQL 难以表达的算法、建模或后处理，不能负责连接数据库、执行 SQL、审计或结果导出。连接信息通过 profile 或 runner 参数传入，密码通过环境变量传入。任何输出形态都必须满足企业 BI 交付标准：查询/导出有 `.meta.json` 元数据和血缘，报告/图表/Dashboard 有统计口径说明、数据血缘/来源、生成时间、证据引用、限制说明和专业版式；每个图表区域都有 `查看数据` 按钮和默认隐藏的对应数据表，并通过 `scripts/validate_output_quality.py`；HTML 还要通过 `scripts/validate_chart.py`。可用 `python scripts/validate_agent_output.py <log-or-text>` 扫描过程输出。本地 DuckDB 计算、明细数据不过大模型、自包含 ECharts 输出、审计与血缘可追踪、专家模式生成企业报告和 Dashboard。\n"
    )


def _wrapper_source(spec: CommandSpec) -> str:
    return (
        _frontmatter(spec.description, spec.argument_hint)
        + f"\n# /echart-{spec.name}\n\n"
        + "Load and execute the echart-skill command below.\n\n"
        + f"@{SOURCE_DIR / '_shared.md'}\n"
        + f"@{SOURCE_DIR / (spec.name + '.md')}\n"
    )


def install() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    CLAUDE_COMMANDS_DIR.mkdir(parents=True, exist_ok=True)

    (SOURCE_DIR / "_shared.md").write_text(_shared_source(), encoding="utf-8")
    for spec in COMMANDS:
        (SOURCE_DIR / f"{spec.name}.md").write_text(_command_source(spec), encoding="utf-8")
        (CLAUDE_COMMANDS_DIR / f"echart-{spec.name}.md").write_text(_wrapper_source(spec), encoding="utf-8")

    print(f"Installed {len(COMMANDS)} Claude Code commands to {CLAUDE_COMMANDS_DIR}")
    print(f"Source command docs: {SOURCE_DIR}")


if __name__ == "__main__":
    install()
