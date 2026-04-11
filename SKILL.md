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
1. Formulate the SQL query. 
2. Execute it via `RunCommand`: `python -c "import duckdb; conn = duckdb.connect('workspace.duckdb'); print(conn.execute('SELECT ...').fetchdf())"`
3. For structural changes, remember the Undo principle: `CREATE TABLE table_name_step2 AS SELECT ...`

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
