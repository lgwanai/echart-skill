---
name: data-skill
description: 专门处理日常办公场景下的高频、复杂数据分析与处理的助手。使用本地代码执行模式（SQL 或 Python + SQLite）来处理数据导入、清洗、查询、提取、合并拆分及报告生成，支持大数据量且保障数据隐私安全。当用户需要处理 Excel/CSV 文件、跨表查询、生成图表或输出数据分析报告时使用此 Skill。
---

# Data Analysis Assistant Workflow

This skill transforms the agent into a powerful local data analysis assistant, strictly adhering to a **Local Code Execution** paradigm.

## Core Architecture & Principles
1. **Local Execution First**: NEVER read large datasets directly into the context window. Always generate Python scripts or SQL commands and execute them locally using `RunCommand`.
2. **SQLite as the Engine**: All CSV/Excel files should be imported into a local SQLite database (default: `workspace.db`). Rely on SQL for robust data manipulation (filtering, joining, grouping).
3. **Non-Destructive Operations (Undo Mechanism)**: Do not overwrite original tables. When modifying data, create a new table (e.g., `CREATE TABLE table_v2 AS SELECT ...`) or a View. This guarantees the user can always say "undo the last step".
4. **Data Privacy**: Keep data local. Only send aggregated statistics or schema info into the context window.

---

## Scenarios & Procedures

### Scenario 1: Data Import & Auto-Cleaning
**Trigger**: User uploads or specifies a CSV/Excel file.
**Action**:
1. Run the built-in importer script:
   ```bash
   python scripts/data_importer.py "path/to/file.xlsx" --db workspace.db
   ```
   *Note: This script calculates the MD5 hash of the file. If an identical file was already imported, it skips the import and returns the existing table name. It also automatically handles merged cells, detects the real header row, chunks large CSVs, and sanitizes column names for SQLite.*
2. Once imported, run a quick check to understand the schema and data:
   ```bash
   sqlite3 workspace.db "PRAGMA table_info(table_name);"
   sqlite3 workspace.db "SELECT * FROM table_name LIMIT 3;" -header -column
   ```
3. Ask the user if they want to perform standard cleaning (e.g., handling missing values, deduplication). Execute these via SQL.

### Scenario 2: Continuous Queries & Manipulation
**Trigger**: User asks to filter, sort, aggregate, or add columns.
**Action**:
1. Formulate the SQL query. 
2. Execute it via `RunCommand`: `sqlite3 workspace.db "SELECT ..."`
3. For structural changes, remember the Undo principle: `CREATE TABLE table_name_step2 AS SELECT ...`

### Scenario 3: Semantic Extraction & Fuzzy Join
**Trigger**: User wants to split addresses, do sentiment analysis, or join tables with mismatched keys (e.g., "Beijing Branch" vs "Beijing Office").
**Action**:
1. Generate a Python script using `pandas` and `sqlite3`.
2. For Fuzzy Joins, use libraries like `thefuzz` or `difflib` in the Python script to match keys, then write the mapping back to SQLite.
3. For Semantic extraction, use regex or heuristic rules in Python. If LLM analysis is strictly required, write a script that processes the column locally or prompts the user for permission to send a sample.

### Scenario 4: Chart Generation
**Trigger**: User requests a visualization (bar, pie, line, scatter, map).
**Action**:
1. Do NOT write custom Python scripts from scratch.
2. Use the built-in universal `scripts/chart_generator.py` script.
3. Formulate the SQL query that aggregates the data correctly (ensure it outputs the exact columns needed for the chart).
4. Construct a JSON configuration string matching this template:
   ```json
   {
       "db_path": "workspace.db",
       "query": "SELECT category, SUM(value) as val FROM table GROUP BY category",
       "chart_type": "bar", // Can be "bar", "pie", "line", "scatter", "map"
       "x_col": "category",
       "y_col": "val",
       "title": "Chart Title",
       "xlabel": "X Axis Label",
       "ylabel": "Y Axis Label",
       "output_path": "tmp/output_chart.html", // Must be .html
       "show_labels": true
   }
   ```
   *Note: If the user requests a map chart (`"chart_type": "map"`), it will utilize the local ECharts and `bmap` extension. The script will check `config.txt` for `BAIDU_AK`. If not found, it will warn the user but fallback to a standard geojson map.*
5. Execute the command:
   ```bash
   python scripts/chart_generator.py --config '{"db_path": "workspace.db", "query": "...", ...}'
   ```
6. The script will automatically start a local HTTP server and return an access URL. Provide this URL to the user to view the interactive chart.

### Scenario 5: File Merging & Splitting
**Trigger**: User needs to combine multiple identical reports or split a master sheet by department.
**Action**:
- **Merge**: Iterate over the files and run `data_importer.py` pointing to the *same* table name (the script appends automatically if the table exists, or write a custom Python script).
- **Split**: Generate a Python script that reads the master table from SQLite and exports it into multiple Excel files using `pandas.DataFrame.to_excel()` inside a loop.

### Scenario 6: Export & Reporting
**Trigger**: User wants to download the final result or generate a summary report.
**Action**:
1. **Export Excel**: Generate a Python script to dump the current SQLite table to `.xlsx`:
   ```python
   import sqlite3
   import pandas as pd
   conn = sqlite3.connect('workspace.db')
   df = pd.read_sql_query("SELECT * FROM final_table", conn)
   df.to_excel('final_output.xlsx', index=False)
   ```
2. **Report Generation**: Write a Markdown file summarizing the analysis steps, key metrics (retrieved via SQL), and referencing any generated charts. Provide the user with the path to the report.

### Scenario 7: Data Cleanup
**Trigger**: Routine maintenance or user request to clean up old data.
**Action**:
1. Run the cleaner script to remove tables and metadata not accessed in the last 30 days:
   ```bash
   python scripts/data_cleaner.py --db workspace.db --days 30
   ```
