---
name: echart-skill
description: 专门处理日常办公场景下的高频、复杂数据分析与处理的助手。使用本地代码执行模式（SQL 或 Python + DuckDB）来处理数据导入、清洗、查询、提取、合并拆分及报告生成，支持大数据量且保障数据隐私安全。当用户需要处理 Excel/CSV 文件、跨表查询、生成图表或输出数据分析报告时使用此 Skill。
---

# Data Analysis Assistant Workflow

This skill transforms the agent into a powerful local data analysis assistant, strictly adhering to a **Local Code Execution** paradigm.

## Core Architecture & Principles
1. **Local Execution First**: NEVER read large datasets directly into the context window. Always generate Python scripts or SQL commands and execute them locally using `RunCommand`.
2. **DuckDB as the Engine**: All CSV/Excel files should be imported into a local DuckDB database (default: `workspace.duckdb`). Rely on SQL for robust data manipulation (filtering, joining, grouping). DuckDB's columnar storage delivers superior analytical performance.
3. **Non-Destructive Operations (Undo Mechanism)**: Do not overwrite original tables. When modifying data, create a new table (e.g., `CREATE TABLE table_v2 AS SELECT ...`) or a View. This guarantees the user can always say "undo the last step".
4. **Data Privacy**: Keep data local. Only send aggregated statistics or schema info into the context window.

---

## Command System

> **双模式支持**: 本 Skill 同时支持**显性指令**和**模糊匹配**。当用户输入以 `/` 开头的指令时，直接执行对应操作；否则进行意图推断。

### 显性指令列表

| 指令 | 别名 | 功能 | 示例 |
|------|------|------|------|
| `/import` | `/i`, `/导入` | 数据导入 | `/import data.xlsx` |
| `/query` | `/q`, `/sql`, `/查询` | 执行 SQL 查询 | `/query SELECT * FROM sales LIMIT 10` |
| `/chart` | `/c`, `/图表`, `/viz` | 生成图表 | `/chart bar 销售额按类别` |
| `/export` | `/e`, `/导出` | 数据导出 | `/export result.csv --table sales` |
| `/tables` | `/t`, `/表`, `/结构` | 查看表结构 | `/tables sales` |
| `/history` | `/h`, `/历史` | 查看导入历史 | `/history --limit 20` |
| `/metrics` | `/m`, `/口径`, `/指标` | 指标管理 | `/metrics add 月活用户` |
| `/help` | `/?`, `/帮助` | 显示帮助 | `/help` |
| `/clean` | `/清理` | 清理旧数据 | `/clean --days 30` |
| `/poll` | `/轮询` | 轮询管理 | `/poll status` |

### 指令处理流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    输入处理流程                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  用户输入                                                        │
│      │                                                          │
│      ▼                                                          │
│  是否以 / 开头？                                                  │
│      │                                                          │
│      ├── 是 ──→ 匹配显性指令 ──→ 直接执行对应 Scenario            │
│      │         │                                                │
│      │         └── 未匹配 ──→ 显示 "未知指令，输入 /help 查看帮助" │
│      │                                                          │
│      └── 否 ──→ 模糊匹配流程                                     │
│                │                                                │
│                ├── 文件上传 ──→ Scenario 1 (数据导入)            │
│                ├── 查询关键词 ──→ Scenario 2 (SQL 查询)           │
│                ├── 图表关键词 ──→ Scenario 4 (图表生成)           │
│                ├── 导出关键词 ──→ Scenario 6 (数据导出)           │
│                └── 其他 ──→ 自然语言理解                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 指令详细说明

#### `/import` - 数据导入
```
/import <文件路径> [--table <表名>] [--db <数据库路径>]
/i <文件路径>  # 别名
/导入 <文件路径>  # 中文别名

示例:
  /import data/sales.xlsx
  /import report.csv --table monthly_report
  /i data.xlsx --db custom.duckdb
```

#### `/query` - SQL 查询
```
/query <SQL语句>
/q <SQL语句>  # 别名
/sql <SQL语句>  # 别名
/查询 <SQL语句>  # 中文别名

示例:
  /query SELECT * FROM sales LIMIT 10
  /q SELECT category, SUM(amount) FROM sales GROUP BY category
  /sql DESCRIBE sales
```

#### `/chart` - 图表生成
```
/chart <图表类型> [描述] [--table <表名>] [--output <路径>]
/c <图表类型> [描述]  # 别名
/图表 <图表类型> [描述]  # 中文别名

支持的图表类型:
  bar, line, pie, scatter, radar, map, funnel, gauge, 
  heatmap, treemap, sunburst, sankey, graph, candlestick,
  line3d, bar3d, scatter3d, surface

示例:
  /chart bar 销售额按类别
  /chart line 月度销售趋势
  /chart pie 各产品占比
  /chart map 各省销售分布
  /c scatter 价格与销量的关系 --table products
```

#### `/export` - 数据导出
```
/export <输出路径> [--table <表名>] [--query <SQL>]
/e <输出路径>  # 别名
/导出 <输出路径>  # 中文别名

示例:
  /export result.csv --table sales
  /export report.xlsx --query "SELECT * FROM sales WHERE year=2024"
  /e output/data.csv
```

#### `/tables` - 查看表结构
```
/tables [表名]
/t [表名]  # 别名
/表 [表名]  # 中文别名
/结构 [表名]  # 中文别名

示例:
  /tables          # 显示所有表
  /tables sales    # 显示 sales 表结构
  /t               # 别名
```

#### `/history` - 查看导入历史
```
/history [--limit <数量>]
/h [--limit <数量>]  # 别名
/历史 [--limit <数量>]  # 中文别名

示例:
  /history          # 显示最近20条
  /history --limit 50
  /h --limit 10
```

#### `/metrics` - 指标管理
```
/metrics [add|list|show] [参数]
/m [操作] [参数]  # 别名
/口径 [操作]  # 中文别名
/指标 [操作]  # 中文别名

示例:
  /metrics list                     # 列出所有指标
  /metrics add 月活用户 --desc "当月至少登录一次的用户"
  /metrics show 月活用户
  /m list
```

#### `/help` - 显示帮助
```
/help
/?  # 别名
/帮助  # 中文别名
```

#### `/clean` - 清理旧数据
```
/clean [--days <天数>] [--db <数据库路径>]
/清理 [--days <天数>]  # 中文别名

示例:
  /clean --days 30    # 清理30天未访问的表
  /clean --days 7
```

#### `/poll` - 轮询管理
```
/poll [list|status|refresh|add|remove] [参数]
/轮询 [操作]  # 中文别名

示例:
  /poll list              # 列出所有轮询任务
  /poll status            # 显示详细状态
  /poll refresh           # 手动刷新所有任务
  /poll add --type http --name api_data --interval 300 --url "https://api.example.com/data"
  /poll remove <job_id>
```

### 模糊匹配关键词

当用户输入不是显性指令时，通过关键词推断意图：

| 意图 | 触发关键词 | 执行 Scenario |
|------|-----------|---------------|
| 数据导入 | 上传、导入、import、load、打开文件、读取 | Scenario 1 |
| SQL 查询 | 查询、筛选、统计、分组、排序、select、group by | Scenario 2 |
| 图表生成 | 图表、可视化、画图、chart、plot、展示、可视化 | Scenario 4 |
| 数据导出 | 导出、下载、export、保存、输出 | Scenario 6 |
| 表结构 | 表结构、字段、列、describe、schema | Scenario 10 |
| 导入历史 | 历史、导入记录、history | Scenario 10 |
| 指标管理 | 指标、口径、定义、metric | Scenario 8 |

---

## SQL Generation Protocol (CRITICAL)

> **重要**: 本项目使用 DuckDB 作为 SQL 引擎，其语法与 MySQL/PostgreSQL 有显著差异。为避免 SQL 执行错误，必须严格遵循以下流程。

### 函数类别索引

DuckDB 支持的 SQL 函数按以下类别组织（详见 `references/SQL_FUNCTIONS_REFERENCE.md`）：

| 类别 | 适用场景 | 典型函数 |
|------|----------|----------|
| **聚合函数** | 求和、计数、平均值、最值 | `SUM`, `COUNT`, `AVG`, `MAX`, `MIN`, `GROUP_CONCAT`→`string_agg` |
| **统计聚合函数** | 方差、标准差、相关性、分位数 | `STDDEV_SAMP`, `VAR_SAMP`, `CORR`, `MEDIAN`, `QUANTILE_CONT` |
| **近似聚合函数** | 大数据近似统计 | `APPROX_COUNT_DISTINCT`, `APPROX_QUANTILE` |
| **数值函数** | 数学计算、取整、三角函数 | `ROUND`, `CEIL`, `FLOOR`, `ABS`, `SQRT`, `POW`, `MOD`→`%` |
| **文本/字符串函数** | 字符串处理、拼接、正则 | `CONCAT`, `SUBSTRING`, `UPPER`, `LOWER`, `LENGTH`, `REGEXP_REPLACE` |
| **日期函数** | 日期计算、格式化 | `DATE_TRUNC`, `DATE_DIFF`, `LAST_DAY`, `STRFTIME`, `EXTRACT` |
| **时间函数** | 时间处理 | `MAKE_TIME`, `DATE_PART` |
| **时间戳函数** | 时间戳操作 | `EPOCH`, `STRPTIME`, `MAKE_TIMESTAMP`, `AGE` |
| **时间间隔函数** | 时间间隔计算 | `TO_DAYS`, `TO_HOURS`, `TO_MINUTES` |
| **窗口函数** | 排名、移动平均、前后值 | `ROW_NUMBER`, `RANK`, `LAG`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE` |
| **列表函数** | 数组/列表操作 | `LIST_VALUE`, `LIST_FILTER`, `LIST_TRANSFORM`, `UNNEST` |
| **条件函数** | 条件判断、NULL处理 | `CASE WHEN`, `COALESCE`, `NULLIF`, `IF` |
| **工具函数** | 类型检查、UUID生成 | `TYPEOF`, `UUID`, `HASH` |

### SQL 生成流程（必须遵循）

```
┌─────────────────────────────────────────────────────────────────┐
│                    SQL 生成智能流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: 需求分析                                                │
│  ├─ 分析用户的查询意图（聚合？过滤？日期计算？字符串处理？）          │
│  └─ 识别涉及的列及其数据类型                                       │
│                                                                 │
│  Step 2: 类别推断                                                │
│  ├─ 根据需求推断需要的函数类别（可多选）                            │
│  └─ 示例：求平均值 + 按月分组 → 聚合函数 + 日期函数                 │
│                                                                 │
│  Step 3: 函数上下文提取                                          │
│  ├─ 读取 SQL_FUNCTIONS_REFERENCE.md 对应类别的函数说明            │
│  └─ 将函数语法和示例作为上下文                                     │
│                                                                 │
│  Step 4: SQL 生成                                                │
│  ├─ 仅使用文档中明确支持的函数                                     │
│  └─ 对于不确定的函数，先查阅文档再使用                              │
│                                                                 │
│  Step 5: 执行验证                                                │
│  ├─ 执行 SQL，检查是否有错误                                      │
│  └─ 如有错误，进入 reAct 修复流程                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 常见 MySQL → DuckDB 函数映射

| MySQL 函数 | DuckDB 替代 | 说明 |
|-----------|-------------|------|
| `GROUP_CONCAT(col, sep)` | `string_agg(col, sep)` | 聚合字符串连接 |
| `IFNULL(a, b)` | `COALESCE(a, b)` 或 `ifnull(a, b)` | NULL 替换 |
| `IF(cond, a, b)` | `if(cond, a, b)` 或 `CASE WHEN` | 条件表达式 |
| `DATE_FORMAT(date, '%Y-%m')` | `strftime(date, '%Y-%m')` | 日期格式化 |
| `DATEDIFF(a, b)` | `date_diff('day', a, b)` | 日期差值 |
| `NOW()` | `CURRENT_TIMESTAMP` 或 `today()` | 当前时间 |
| `SUBSTRING(str, pos, len)` | `substring(str, pos, len)` | 子串（1-based） |
| `CONCAT_WS(sep, a, b)` | `concat_ws(sep, a, b)` | 带分隔符连接 |
| `FIND_IN_SET(str, list)` | `list_contains(string_split(list, ','), str)` | 列表查找 |
| `REGEXP_LIKE(str, pattern)` | `regexp_matches(str, pattern)` | 正则匹配 |
| `MOD(a, b)` | `a % b` | 取模运算 |
| `POWER(x, y)` | `pow(x, y)` 或 `x ** y` | 幂运算 |

### reAct 错误修复流程

当 SQL 执行出错时，按照以下 reAct 循环进行修复：

```
┌─────────────────────────────────────────────────────────────────┐
│                    reAct 修复循环                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Thought: 分析错误信息                                         │
│     ├─ 错误类型：函数不存在？语法错误？类型不匹配？                  │
│     └─ 定位问题：哪个函数/语法导致了错误？                         │
│                                                                 │
│  2. Action: 查阅文档                                              │
│     ├─ 在 SQL_FUNCTIONS_REFERENCE.md 中搜索正确函数               │
│     └─ 或搜索类别索引找到替代方案                                  │
│                                                                 │
│  3. Observation: 确认修复方案                                     │
│     ├─ 验证新函数的语法和参数                                      │
│     └─ 确保与 DuckDB 兼容                                         │
│                                                                 │
│  4. Retry: 重新执行                                               │
│     ├─ 应用修复后的 SQL                                           │
│     └─ 如仍有错误，返回 Step 1                                     │
│                                                                 │
│  5. Fallback: 最多 3 次重试                                       │
│     ├─ 3 次失败后，考虑使用 Python + pandas 替代                   │
│     └─ 或向用户说明限制，寻求替代需求                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 示例：完整 SQL 生成过程

**用户需求**: "统计每个产品类别的月销售额，找出销售额前10的月份"

**Step 1 - 需求分析**:
- 聚合：按类别和月份分组求和
- 日期处理：从日期字段提取月份
- 排序：按销售额降序
- 限制：取前10

**Step 2 - 类别推断**:
- 聚合函数 → `SUM`, `GROUP BY`
- 日期函数 → `date_trunc` 或 `strftime`
- 窗口函数（可选）→ `ROW_NUMBER` 或直接用 `ORDER BY + LIMIT`

**Step 3 - 提取函数上下文**:
```markdown
# 从 SQL_FUNCTIONS_REFERENCE.md 读取：
- date_trunc(part, date) - 截断到指定精度
- SUM(arg) - 求和
- string_agg(arg, sep) - 字符串聚合
```

**Step 4 - 生成 SQL**:
```sql
SELECT 
    category,
    date_trunc('month', sale_date) as month,
    SUM(amount) as total_sales
FROM sales
GROUP BY category, date_trunc('month', sale_date)
ORDER BY total_sales DESC
LIMIT 10;
```

**Step 5 - 执行验证**: 
- 成功 → 返回结果
- 失败 → 进入 reAct 流程

---

## Scenarios & Procedures

### Scenario 1: Data Import & Auto-Cleaning
**Trigger**: User uploads or specifies a CSV/Excel/WPS(.et)/Numbers file.
**Action**:
1. Run the built-in importer script (supports `.csv`, `.xlsx`, `.xls`, `.et`, `.numbers`):
   ```bash
   python scripts/data_importer.py "path/to/file.xlsx" --db workspace.duckdb
   ```
   *Note: This script calculates the MD5 hash of the file. If an identical file was already imported, it skips the import and returns the existing table name. It also automatically handles merged cells, detects the real header row, chunks large CSVs, and sanitizes column names for DuckDB.*
2. Once imported, run a quick check to understand the schema and data:
   ```bash
   python -c "import duckdb; conn = duckdb.connect('workspace.duckdb'); print(conn.execute('DESCRIBE table_name').fetchdf())"
   python -c "import duckdb; conn = duckdb.connect('workspace.duckdb'); print(conn.execute('SELECT * FROM table_name LIMIT 3').fetchdf())"
   ```
3. Ask the user if they want to perform standard cleaning (e.g., handling missing values, deduplication). Execute these via SQL.

### Scenario 2: Continuous Queries & Manipulation
**Trigger**: User asks to filter, sort, aggregate, or add columns.
**Action**:
1. **SQL Generation with Function Validation**: Follow the intelligent SQL generation workflow (see `SQL Generation Protocol` section below).
2. Execute it via `RunCommand`: `python -c "import duckdb; conn = duckdb.connect('workspace.duckdb'); print(conn.execute('SELECT ...').fetchdf())"`
3. For structural changes, remember the Undo principle: `CREATE TABLE table_name_step2 AS SELECT ...`
4. **Error Handling**: If SQL execution fails, use the reAct recovery process (see `SQL Error Recovery (reAct)` section below).

### Scenario 3: Semantic Extraction & Fuzzy Join
**Trigger**: User wants to split addresses, do sentiment analysis, or join tables with mismatched keys (e.g., "Beijing Branch" vs "Beijing Office").
**Action**:
1. Generate a Python script using `pandas` and `duckdb`.
2. For Fuzzy Joins, use libraries like `thefuzz` or `difflib` in the Python script to match keys, then write the mapping back to DuckDB.
3. For Semantic extraction, use regex or heuristic rules in Python. If LLM analysis is strictly required, write a script that processes the column locally or prompts the user for permission to send a sample.

### Scenario 4: Chart Generation
**Trigger**: User requests a visualization (bar, pie, line, scatter, map, funnel, 3D charts, Gantt, etc.).
**Action**:
1. Do NOT write custom Python scripts from scratch.
2. We have a powerful template-based rendering engine. Use the built-in `scripts/chart_generator.py` script.
3. This skill provides **100% support for all ECharts v6.0 chart types**. First, identify the required chart type. Look into `references/prompts/` directory to find the corresponding Prompt skeleton for the exact chart type (e.g., `references/prompts/line/stacked_area.md`). Read the prompt to understand the data structure requirements.
4. Formulate the SQL query that aggregates the data correctly according to the prompt's requirements.
5. Generate the `custom_js` and `echarts_option` based on the prompt template.
6. Construct a JSON configuration file (save it in `outputs/configs/`) matching this structure:
   ```json
    {
        "db_path": "workspace.duckdb",
       "query": "SELECT category, SUM(value) as val FROM table GROUP BY category",
       "title": "Chart Title",
       "output_path": "/Users/wuliang/workspace/echart-skill/outputs/html/output_chart.html",
       "echarts_option": { ... }, // Generated option from prompt
       "custom_js": "..." // Optional JS logic for complex data binding
   }
   ```
   *Note: All chart JS dependencies (like `echarts.min.js`, `china.js`, `bmap.min.js`) MUST use the local relative paths injected by the Python generator. DO NOT include any `<script src="https://cdn...">` remote links in the generated code to ensure offline support. Output files MUST be stored in the isolated `outputs/html/` directory.*
   *CRITICAL ECHARTS RULE: The ECharts `pie` series DOES NOT support `coordinateSystem: 'geo'`. If the user asks to display data on a map, you MUST use `scatter` or `effectScatter` series with bubble sizes representing the values. NEVER attempt to put a pie chart on a geo map directly.*
   *MAP FALLBACK RULE: For map-based charts, prioritize using local static maps (`china`, `world`, or specific province names). If the user needs to visualize data at a granularity not supported by local static JS (e.g., city-level dimensions without a corresponding local map, street-level data, or specific foreign countries not fully detailed in the world map), you MUST fallback to using ECharts `bmap` mode (Baidu Map API). This requires an AK (`ak` mode).*
   *BAIDU AK RULE: If the user provides a Baidu Map AK, remember that there are two types of APIs: 1) JavaScript API (Frontend) and 2) Geocoding API (Backend Python). If the backend Python geocoding fails with "status 240", it means the AK is a Browser-type AK and lacks Backend Geocoding permissions. In this case, you should either fallback to hardcoded coordinates in JS or ask the user to provide a "Server-side" AK.*
   *GANTT CHART RULE: Gantt charts use a dedicated simplified API (see Scenario 9) rather than the template-based approach. Use `scripts/gantt_chart.py` with `generate_gantt_chart()` for timeline visualizations.*
7. Execute the command:
   ```bash
   python scripts/chart_generator.py --config outputs/configs/your_config.json
   ```
8. The script will automatically start a local HTTP server and return an access URL. Provide this URL to the user to view the interactive chart.

### Scenario 5: File Merging & Splitting
**Trigger**: User needs to combine multiple identical reports or split a master sheet by department.
**Action**:
- **Merge**: Iterate over the files and run `data_importer.py` pointing to the *same* table name (the script appends automatically if the table exists, or write a custom Python script).
- **Split**: Generate a Python script that reads the master table from DuckDB and exports it into multiple Excel files using `pandas.DataFrame.to_excel()` inside a loop.

### Scenario 6: Export & Reporting
**Trigger**: User wants to download the final result or generate a summary report.
**Action**:
1. **Export CSV/Excel**: Use the built-in exporter script to dump a table or query result to `.csv` or `.xlsx`:
   ```bash
   # Export an entire table
   python scripts/data_exporter.py "outputs/final_result.csv" --table "final_table"
   
   # Export a specific query
   python scripts/data_exporter.py "outputs/final_result.xlsx" --query "SELECT category, SUM(value) FROM sales GROUP BY category"
   ```
2. **Report Generation**: Write a Markdown file summarizing the analysis steps, key metrics (retrieved via SQL), and referencing any generated charts. Provide the user with the path to the report.

### Scenario 7: Data Cleanup
**Trigger**: Routine maintenance or user request to clean up old data.
**Action**:
1. Run the cleaner script to remove tables and metadata not accessed in the last 30 days:
   ```bash
   python scripts/data_cleaner.py --db workspace.duckdb --days 30
   ```

### Scenario 8: Metrics Management
**Trigger**: User describes or defines a specific metric calculation logic or business definition (口径).
**Action**:
1. When the user provides a metric definition, save it to the local markdown file `references/metrics.md` to build up context for future SQL generation.
2. Use the built-in script `scripts/metrics_manager.py` to append the metric:
   ```bash
   python scripts/metrics_manager.py --name "Metric Name" --desc "Metric calculation logic or business description"
   ```
3. When generating SQL queries later, ALWAYS read `references/metrics.md` to ensure the generated SQL aligns with the saved business definitions.

### Scenario 9: Gantt Chart Generation
**Trigger**: User requests project timeline or task schedule visualization.
**Action**:
1. Use the built-in Gantt chart wrapper for simplified API:
   ```python
   from scripts.gantt_chart import generate_gantt_chart

   config = {
       "title": "Project Timeline",
       "tasks": [
           {"name": "Design", "start": "2024-01-01", "end": "2024-01-15"},
           {"name": "Development", "start": "2024-01-10", "end": "2024-02-01"},
           {"name": "Testing", "start": "2024-01-25", "end": "2024-02-10"}
       ]
   }
   output_path = generate_gantt_chart(config)
   ```
2. The generated HTML will open in browser with interactive Gantt chart.
3. Tasks support optional fields:
   - `category`: For grouping tasks in rows
   - `color`: Custom bar color (hex code)

**Note**: Dates can be ISO strings or datetime objects. End date must be after start date.

### Scenario 10: View Import History & Table Structure
**Trigger**: User asks to view import history, check table structures, or see table relationships.
**Action**:
1. **查看导入历史**: Run `python scripts/data_importer.py history --db workspace.duckdb [--limit 20]`
2. **查看指定表结构**: Run `python scripts/data_importer.py structure --db workspace.duckdb --table TABLE_NAME`
3. **查看所有表结构**: Run `python scripts/data_importer.py structure --db workspace.duckdb`
4. **查看表关联关系**: Run `python scripts/data_importer.py relationships --db workspace.duckdb`
5. **一键查看全部**: Run `python scripts/data_importer.py show --db workspace.duckdb`

**Example output**:
```
## 导入历史

| 文件名           | 表名      | 行数 | 导入时间            | 文件路径              |
| -------------- | ------- | -- | --------------- | ----------------- |
| sales.xlsx     | sales   | 1500 | 2026-04-11 10:30 | /path/to/sales.xlsx |

## 表结构: sales

**行数:** 1500

| 列名   | 类型      | 可空  |
| ---- | ------- | --- |
| id   | VARCHAR | YES |
| name | VARCHAR | NO  |
```

### Scenario 11: Export Charts for Offline Sharing
**Trigger**: User wants to share charts/dashboards as standalone HTML files that work offline.

**Action**:

**Export Chart:**
```python
from scripts.chart_generator import export_standalone_chart

config = {
    "db_path": "workspace.duckdb",
    "query": "SELECT category, value FROM sales",
    "title": "Sales by Category",
    "echarts_option": {
        "xAxis": {"type": "category"},
        "yAxis": {"type": "value"},
        "series": [{"type": "bar"}]
    }
}
export_standalone_chart(config, "sales_chart.html", theme="default")
```

**Export Dashboard:**
```python
from scripts.dashboard_generator import export_standalone_dashboard

export_standalone_dashboard("dashboard_config.json", "my_dashboard.html")
```

**Export Gantt Chart:**
```python
from scripts.gantt_chart import export_standalone_gantt

config = {
    "title": "Project Timeline",
    "tasks": [
        {"name": "Design", "start": "2024-01-01", "end": "2024-01-15"},
        {"name": "Development", "start": "2024-01-10", "end": "2024-02-01"},
        {"name": "Testing", "start": "2024-02-01", "end": "2024-02-15"},
    ]
}
export_standalone_gantt(config, "project_timeline.html", theme="dark")
```

**Key Features:**
- Exported files are self-contained (~1.2MB with ECharts library)
- Work offline without any server
- Can be shared via email or file transfer
- Open in any modern browser
- Support themes: `default`, `dark`

### Scenario 12: CLI Export (Command Line)
**Trigger**: User needs to export charts via command line for batch processing or automation.

**Export Chart:**
```bash
# Basic usage (auto-generates filename with timestamp)
python scripts/chart_cli.py export-chart config.json

# Specify output path
python scripts/chart_cli.py export-chart config.json --output reports/sales.html

# Use dark theme
python scripts/chart_cli.py export-chart config.json --theme dark
```

**Export Dashboard:**
```bash
python scripts/chart_cli.py export-dashboard dashboard_config.json

# With custom output
python scripts/chart_cli.py export-dashboard dashboard_config.json --output monthly_report.html --theme dark
```

**Export Gantt Chart:**
```bash
# Gantt chart config is a JSON array of tasks
python scripts/chart_cli.py export-gantt tasks.json --title "项目进度"

# With output path
python scripts/chart_cli.py export-gantt tasks.json --title "Project Timeline" --output timeline.html
```

**Config File Format (for export-chart):**
```json
{
    "title": "销售数据图表",
    "db_path": "workspace.duckdb",
    "query": "SELECT category, SUM(amount) as total FROM sales GROUP BY category",
    "echarts_option": {
        "xAxis": {"type": "category"},
        "yAxis": {"type": "value"},
        "series": [{"type": "bar"}]
    }
}
```

**Gantt Task Config Format (for export-gantt):**
```json
[
    {"name": "需求分析", "start": "2024-01-01", "end": "2024-01-15"},
    {"name": "系统设计", "start": "2024-01-10", "end": "2024-01-25"},
    {"name": "开发实现", "start": "2024-01-20", "end": "2024-02-20"}
]
```

**Command Parameters:**
- `<config>`: Config file path (JSON format)
- `--output`, `-o`: Output HTML path (optional, default: `{title}_{timestamp}.html`)
- `--theme`: Chart theme (`default` or `dark`, default: `default`)
- `--title`: Gantt chart title (export-gantt only)

**View Help:**
```bash
python scripts/chart_cli.py --help
python scripts/chart_cli.py export-chart --help
```

**Batch Export Example:**
```bash
# Export multiple charts
for config in outputs/configs/*.json; do
    python scripts/chart_cli.py export-chart "$config"
done

# Automated daily report
python scripts/chart_cli.py export-dashboard daily_dashboard.json \
    --output "reports/report_$(date +%Y%m%d).html"
```

**Notes:**
- Exported HTML files work offline (ECharts library embedded)
- File size ~1.2MB per export (includes ECharts library)
- Chinese characters are preserved correctly
- Generated filename format: `{sanitized_title}_{YYYYMMDD_HHMMSS}.html`

### Scenario 13: External Database Connections
**Trigger**: User needs to query data from MySQL, PostgreSQL, MongoDB, or SQLite databases.

**Action:**

**1. Configure Connections (db_connections.json):**
```json
{
    "connections": {
        "mysql_prod": {
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "database": "production",
            "username": "admin",
            "password": "${MYSQL_PASSWORD}"
        },
        "postgres_analytics": {
            "type": "postgresql",
            "host": "analytics-db.internal",
            "database": "analytics",
            "username": "reader",
            "password": "${PG_PASSWORD}"
        },
        "mongo_docs": {
            "type": "mongodb",
            "connection_string": "${MONGODB_URI}"
        },
        "sqlite_local": {
            "type": "sqlite",
            "database": "/path/to/local.db"
        }
    }
}
```

**2. Set Environment Variables for Secrets:**
```bash
export MYSQL_PASSWORD=your_password
export PG_PASSWORD=your_password
export MONGODB_URI="mongodb://user:pass@localhost:27017/docs"
```

**3. Query Database:**
```bash
# Execute SQL query
python scripts/db_cli.py query mysql_prod "SELECT * FROM orders WHERE date > '2024-01-01'"

# Query from file
python scripts/db_cli.py query postgres_analytics --file queries/monthly_sales.sql --output json

# MongoDB query (requires --collection)
python scripts/db_cli.py query mongo_docs '{"status": "active"}' --collection users
```

**4. Discover Schema:**
```bash
# List tables
python scripts/db_cli.py list-tables mysql_prod

# List PostgreSQL tables in specific schema
python scripts/db_cli.py list-tables postgres_analytics --schema public

# Describe table structure
python scripts/db_cli.py describe-table mysql_prod users

# MongoDB: list databases
python scripts/db_cli.py list-tables mongo_docs --show-databases

# MongoDB: list collections
python scripts/db_cli.py list-tables mongo_docs --database docs

# MongoDB: infer collection schema
python scripts/db_cli.py describe-table mongo_docs users
```

**5. Import to DuckDB:**
```bash
# Import SQL query results to DuckDB
python scripts/db_cli.py import mysql_prod "SELECT * FROM customers" --table-name customers_import

# Import with custom DuckDB path
python scripts/db_cli.py import postgres_analytics "SELECT * FROM sales" --duckdb analytics.duckdb

# Import MongoDB collection
python scripts/db_cli.py import mongo_docs '{}' --collection users --table-name mongo_users
```

**6. After Import, Use with Charts:**
```json
{
    "db_path": "workspace.duckdb",
    "query": "SELECT * FROM customers_import",
    "title": "Imported Customers",
    "echarts_option": {
        "xAxis": {"type": "category"},
        "yAxis": {"type": "value"},
        "series": [{"type": "bar"}]
    }
}
```

**Key Features:**
- Connection config auto-discovered in current and parent directories
- Use `${ENV_VAR}` placeholders for passwords (never hardcode secrets)
- Query results automatically import to DuckDB with `import` command
- Large results (>10K rows) are streamed
- Metadata tracked in `_data_skill_meta` table
- Support for MySQL, PostgreSQL, SQLite (via SQLAlchemy), and MongoDB (via PyMongo)

**Notes:**
- Default connection timeout: 30 seconds (override with `--timeout`)
- MongoDB documents are flattened for tabular storage (nested fields become `parent_child`)
- Arrays in MongoDB are expanded to indexed fields (`skills_0`, `skills_1`)

### Scenario 14: Polling & Auto-Refresh
**Trigger**: User needs to automatically refresh data from HTTP APIs or databases on a schedule.

**Action:**

**1. Create Polling Configuration (polling_config.json):**
```json
{
    "jobs": [
        {
            "source_type": "http",
            "source_name": "sales_api",
            "interval_seconds": 300,
            "table_name": "live_sales",
            "http_config": {
                "url": "https://api.example.com/sales",
                "format": "json",
                "auth": {"type": "bearer", "token": "${API_TOKEN}"}
            }
        },
        {
            "source_type": "database",
            "source_name": "production_db",
            "interval_seconds": 600,
            "table_name": "live_orders",
            "db_profile": "mysql_prod",
            "query": "SELECT * FROM orders WHERE created_at > NOW() - INTERVAL 1 HOUR"
        }
    ]
}
```

**2. Manage Polling Jobs:**
```bash
# List all polling jobs
python scripts/polling_cli.py list

# Show detailed status
python scripts/polling_cli.py status
python scripts/polling_cli.py status <job_id>

# Manual refresh (trigger immediately)
python scripts/polling_cli.py refresh
python scripts/polling_cli.py refresh <job_id>

# Add new polling job
python scripts/polling_cli.py add --type http --name "my_api" --interval 300 --table api_data --http-config '{"url": "https://api.example.com/data", "format": "json"}'

# Remove polling job
python scripts/polling_cli.py remove <job_id>
```

**3. Use Polled Data in Charts:**
```json
{
    "db_path": "workspace.duckdb",
    "query": "SELECT * FROM live_sales ORDER BY timestamp DESC LIMIT 100",
    "title": "Live Sales Data",
    "echarts_option": {
        "xAxis": {"type": "category"},
        "yAxis": {"type": "value"},
        "series": [{"type": "line", "smooth": true}]
    }
}
```

**Key Features:**
- APScheduler-based background polling
- HTTP sources with all auth types (Basic, Bearer, API Key, OAuth2)
- Database polling for MySQL, PostgreSQL, MongoDB, SQLite
- Automatic DuckDB table updates
- Last refresh timestamp tracked in `_data_skill_meta`
- Manual refresh on-demand
- Error counting and status tracking

**Notes:**
- Minimum interval: 10 seconds
- Maximum interval: 86400 seconds (24 hours)
- Polling runs in background thread
- Tables are replaced on each poll (not appended)
