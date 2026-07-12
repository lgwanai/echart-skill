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
    CommandSpec("query", "/query", "执行本地 DuckDB SQL 查询", "<SQL>", "使用本地 DuckDB 执行查询；不要把大表明细读入模型上下文，只返回必要聚合或样例。", ("/echart-query SELECT * FROM sales LIMIT 10",)),
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
    CommandSpec("dbconn", "/dbconn", "管理数据库连接配置", "add|list|test|import ...", "管理 MySQL/PostgreSQL/MongoDB/SQLite 连接，支持全局/项目级连接配置。", ("/echart-dbconn list",)),
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
    return (
        _frontmatter(spec.description, spec.argument_hint)
        + f"\n# /echart-{spec.name}\n\n"
        + f"映射到 echart-skill 原始指令 `{spec.original}`。\n\n"
        + f"## 任务\n\n{spec.detail}\n\n"
        + "## 执行规则\n\n"
        + "1. 使用 echart-skill 的本地优先数据分析流程。\n"
        + "2. 不把大表明细读入模型上下文；使用 DuckDB/Python 在本地计算。\n"
        + "3. 生成报告、Dashboard、图表或导出后，按需要记录审计和血缘。\n"
        + "4. 对图表/Dashboard/Report HTML 运行 `python scripts/validate_chart.py <file>` 质量门。\n"
        + "5. 如需完整流程细节，读取仓库根目录 `SKILL.md` 中对应指令章节。\n"
        + "6. 用户在本命令后的参数作为原始指令参数处理：`$ARGUMENTS`。\n\n"
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
        "核心原则：本地 DuckDB 计算、明细数据不过大模型、自包含 ECharts 输出、审计与血缘可追踪、专家模式生成企业报告和 Dashboard。\n"
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
