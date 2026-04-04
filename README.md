# Echart Skill

专门为 AI Agent 设计的本地数据分析与处理技能包（Skill），旨在解决日常办公场景下的高频、复杂数据分析任务。

## 项目亮点

- 🛡️ **绝对安全的数据隐私**：摒弃了将原始数据或大文件直接发给大模型分析的传统方式。本技能要求 Agent 在本地存储数据（SQLite），并在本地生成代码进行解析和计算。数据绝不出域，最大程度保障企业隐私。
- 📊 **全量图表支持 (ECharts 6.0)**：内置数百种 ECharts 官方图表 Prompt 模板，**100% 覆盖并支持 [ECharts 官方示例](https://echarts.apache.org/examples/zh/index.html) 中所有的图表绘制类型**。无论是基础的折柱饼、散点图，还是复杂的 3D 气泡图、关系图、桑基图、漏斗图，亦或是包含全国/全球静态离线地图的高级地理可视化，Agent 都能直接生成可交互的纯本地 HTML 页面。
- 🤖 **Agent 原生设计**：专为自动化智能体打造的"操作说明书"，约束了 Agent 在面对复杂数据时的行为边界和操作规范。
- 🤝 **广泛的兼容性**：支持主流的基于本地执行的 Agent 平台，包括但不限于 **OpenClaw, Claude Code, WorkBuddy, OpenCode, Trae** 等。
- ⚡ **强大的"脏表"处理能力**：内置专门的 Python 导入器，能自动识别复杂表头，自动打平合并单元格，从容应对真实办公场景中的非标准 Excel 文件。

## 为什么要这个 Skill？

在日常办公中，我们经常需要处理几十万行的 CSV 或结构复杂的 Excel。
如果直接让大模型处理：
1. **Token 限制与成本**：大文件根本无法完整塞入对话上下文，且消耗极其昂贵。
2. **隐私泄漏风险**：将客户清单、财务报表等敏感数据发给云端模型是极其危险的。
3. **容易把表搞坏**：大模型如果不加约束地直接用 Pandas 修改原表，一旦出错很难撤销。

**Echart Skill 就是为了解决这些痛点而生**。它教导 Agent 如何在本地搭建轻量级的 SQLite 数据库，如何进行安全的增删改查，以及如何留下"后悔药（Undo）"机制。

## 使用场景

- **智能数据导入**：全面兼容 `.csv`, `.xlsx`, `.xls`，以及 **WPS 数据文件 (`.et`)** 和 **Mac Numbers 文件 (`.numbers`)**。支持自动遍历并拆分导入所有工作表（Sheets）。超大文件自动分块（Chunking）导入，避免 OOM。
- **对话式持续查询**：通过自然语言让 Agent 帮你进行筛选、排序、分组求和等连续操作。
- **业务口径管理**：提供专门的统计口径和指标定义管理能力，持久化保存用户的业务规则，为大模型生成高准确度的 SQL 提供稳定上下文。
- **语义提取与模糊匹配**：利用 Python 结合大模型能力，从杂乱的地址列提取省市，或将两张命名不一致的表（如"北京分公司"与"北京市分部"）进行模糊关联。
- **全栈图表生成与报告**：直接生成纯本地交互式的 ECharts 图表，**支持数百种 ECharts 6.0 官方图表类型**。支持折线图、柱状图、饼图、散点图、雷达图、K线图、热力图、树图、旭日图、桑基图、漏斗图、仪表盘、3D图表以及带地理坐标的地图。内置中国省市及世界地图离线资源，完美支持断网环境下的数据可视化。
- **一键导出与合并拆分**：支持将任意 SQL 查询结果或整表快速导出为 `.csv` 或 `.xlsx`。自动合并多月同构报表，或按"部门"将总表一键拆分导出为多个独立文件。
- **多图表仪表盘**：通过简单的 JSON 配置文件，一键生成包含多个图表的交互式仪表盘，支持灵活的网格布局和图表定位。
- **URL 数据源接入**：支持直接从 HTTP/HTTPS URL 导入 JSON 或 CSV 数据，支持 Basic Auth 和 Bearer Token 认证，并可手动刷新数据源。
- **甘特图支持**：提供简化的甘特图 API，只需提供任务名称、开始时间和结束时间，即可生成专业的项目进度可视化图表。
- **表格合并能力**：支持将多个 SQLite 表格合并为一个，并导出为 CSV/Excel 文件或保存为新的数据库表。

## 核心工作流

1. **导入拦截**：收到文件后，Agent 会调用内置的 `scripts/data_importer.py` 脚本，将数据清洗、规整后安全写入本地 `workspace.db` (SQLite)。
2. **本地探查**：Agent 使用 SQL 探查表结构（Schema）和部分统计信息，而不是读取所有行。
3. **非破坏性操作**：当收到修改指令时，Agent 会生成 SQL 或 Python 脚本在本地运行。并且必须通过创建新表或视图（如 `CREATE TABLE v2 AS SELECT...`）来执行，确保原始数据不被污染。
4. **结果输出**：根据要求，将处理好的数据重新导出为干净的 Excel，或生成可视化图表。对于地图类需求，优先使用本地静态地图，遇到精细维度则自动降级启用百度 AK 渲染模式。

---

## 场景示例详解

### 场景 1：数据导入与自动清洗

**触发条件**：用户上传或指定 CSV/Excel/WPS/Numbers 文件。

**操作步骤**：

1. 运行内置导入脚本：
   ```bash
   python scripts/data_importer.py "path/to/file.xlsx" --db workspace.db
   ```
   
   > **说明**：脚本自动计算文件 MD5，相同文件跳过重复导入。支持合并单元格处理、智能表头检测、大文件分块、列名规范化。

2. 导入后快速检查数据结构：
   ```bash
   sqlite3 workspace.db "PRAGMA table_info(table_name);"
   sqlite3 workspace.db "SELECT * FROM table_name LIMIT 3;" -header -column
   ```

3. 询问用户是否需要标准清洗（缺失值处理、去重等），通过 SQL 执行。

---

### 场景 2：持续查询与数据操作

**触发条件**：用户要求筛选、排序、聚合或添加列。

**操作步骤**：

1. 编写 SQL 查询语句
2. 通过命令执行：`sqlite3 workspace.db "SELECT ..."`
3. 结构变更遵循 Undo 原则：`CREATE TABLE table_name_step2 AS SELECT ...`

**示例**：
```bash
# 筛选销售额前10的产品
sqlite3 workspace.db "SELECT product, SUM(amount) as total FROM sales GROUP BY product ORDER BY total DESC LIMIT 10;"

# 创建清洗后的新表
sqlite3 workspace.db "CREATE TABLE sales_clean AS SELECT * FROM sales WHERE amount > 0;"
```

---

### 场景 3：语义提取与模糊关联

**触发条件**：用户需要拆分地址、情感分析，或关联命名不一致的表。

**操作步骤**：

1. 生成 Python 脚本使用 `pandas` 和 `sqlite3`
2. 模糊关联使用 `thefuzz` 或 `difflib` 库匹配键值
3. 语义提取使用正则或启发式规则

**示例 - 地址提取**：
```python
import pandas as pd
import sqlite3
import re

conn = sqlite3.connect('workspace.db')
df = pd.read_sql_query("SELECT * FROM customers", conn)

# 提取省市
def extract_province(address):
    match = re.search(r'(北京|上海|广东|江苏|浙江)', address)
    return match.group(1) if match else '未知'

df['province'] = df['address'].apply(extract_province)
df.to_sql('customers_with_province', conn, if_exists='replace', index=False)
```

---

### 场景 4：图表生成

**触发条件**：用户请求可视化（柱状图、饼图、折线图、地图、漏斗图、3D图表、甘特图等）。

**操作步骤**：

1. 确定图表类型，查看 `references/prompts/` 目录下对应的 Prompt 模板
2. 编写聚合数据的 SQL 查询
3. 生成 `echarts_option` 和 `custom_js`
4. 创建 JSON 配置文件：

   ```json
   {
       "db_path": "workspace.db",
       "query": "SELECT category, SUM(value) as val FROM table GROUP BY category",
       "title": "销售分类统计",
       "output_path": "outputs/html/sales_chart.html",
       "echarts_option": {
           "xAxis": {"type": "category"},
           "yAxis": {"type": "value"},
           "series": [{"type": "bar"}]
       }
   }
   ```

5. 执行生成命令：
   ```bash
   python scripts/chart_generator.py --config outputs/configs/sales_config.json
   ```

**支持的图表类型**：
- 基础图表：`bar`（柱状图）、`line`（折线图）、`pie`（饼图）、`scatter`（散点图）
- 统计图表：`radar`（雷达图）、`boxplot`（箱线图）、`heatmap`（热力图）
- 关系图表：`graph`（关系图）、`sankey`（桑基图）、`chord`（和弦图）
- 层级图表：`tree`（树图）、`treemap`（矩形树图）、`sunburst`（旭日图）
- 地理图表：`map`（地图）、`lines`（线图）
- 3D 图表：`bar3D`、`line3D`、`scatter3D`、`surface`
- 专业图表：`candlestick`（K线图）、`gauge`（仪表盘）、`funnel`（漏斗图）
- 时间图表：`calendar`（日历图）、`themeRiver`（主题河流图）

> **重要规则**：
> - 所有图表依赖使用本地路径，禁用 CDN 远程链接
> - 输出文件必须存储在 `outputs/html/` 目录
> - 饼图不支持地理坐标系，地图上必须使用 `scatter` 或 `effectScatter`
> - 地图优先使用本地静态地图，精细维度自动降级到百度地图 API

---

### 场景 5：文件合并与拆分

**触发条件**：用户需要合并多个相同结构的报表，或按维度拆分主表。

**合并操作**：
```bash
# 方式1：连续导入到同一表
python scripts/data_importer.py "report_jan.xlsx" --db workspace.db --table monthly_report
python scripts/data_importer.py "report_feb.xlsx" --db workspace.db --table monthly_report

# 方式2：使用数据合并脚本
python scripts/data_merger.py --tables report_jan report_feb report_mar --target merged_report --db workspace.db
```

**拆分操作**：
```python
import pandas as pd
import sqlite3

conn = sqlite3.connect('workspace.db')
df = pd.read_sql_query("SELECT * FROM master_table", conn)

# 按部门拆分
for dept in df['department'].unique():
    dept_df = df[df['department'] == dept]
    dept_df.to_excel(f'outputs/{dept}_report.xlsx', index=False)
```

---

### 场景 6：导出与报告生成

**触发条件**：用户需要下载结果或生成分析报告。

**导出 CSV/Excel**：
```bash
# 导出整表
python scripts/data_exporter.py "outputs/final_result.csv" --table "final_table"

# 导出查询结果
python scripts/data_exporter.py "outputs/summary.xlsx" --query "SELECT category, SUM(value) FROM sales GROUP BY category"
```

**生成分析报告**：
1. 编写 Markdown 文件总结分析步骤
2. 通过 SQL 获取关键指标
3. 引用生成的图表
4. 提供报告路径给用户

---

### 场景 7：数据清理

**触发条件**：定期维护或用户请求清理旧数据。

**操作命令**：
```bash
# 清理30天未访问的表
python scripts/data_cleaner.py --db workspace.db --days 30
```

---

### 场景 8：业务口径管理

**触发条件**：用户定义指标计算逻辑或业务定义。

**保存口径**：
```bash
python scripts/metrics_manager.py --name "月活跃用户" --desc "当月至少登录一次的用户数量，按user_id去重统计"
```

**使用口径**：
生成 SQL 前读取 `references/metrics.md`，确保计算逻辑与业务定义一致。

---

### 场景 9：甘特图生成

**触发条件**：用户请求项目时间线或任务进度可视化。

**使用简化 API**：
```python
from scripts.gantt_chart import generate_gantt_chart, GanttChartConfig, GanttTask

config = GanttChartConfig(
    title="项目开发进度",
    tasks=[
        GanttTask(name="需求分析", start="2024-01-01", end="2024-01-15"),
        GanttTask(name="系统设计", start="2024-01-10", end="2024-01-25"),
        GanttTask(name="开发实现", start="2024-01-20", end="2024-02-20"),
        GanttTask(name="测试部署", start="2024-02-15", end="2024-02-28"),
    ],
    output_path="outputs/html/project_gantt.html"
)
output_path = generate_gantt_chart(config)
```

**支持的字段**：
- `name`（必填）：任务名称
- `start`（必填）：开始日期，支持 ISO 字符串或 datetime 对象
- `end`（必填）：结束日期，必须晚于开始日期
- `category`（可选）：任务分类，用于分组显示
- `color`（可选）：自定义颜色（十六进制）

---

### 场景 10：仪表盘生成

**触发条件**：用户需要多图表组合展示。

**创建配置文件** `outputs/configs/dashboard.json`：
```json
{
    "title": "销售数据概览",
    "columns": 2,
    "row_height": 400,
    "gap": 16,
    "charts": [
        {
            "id": "chart1",
            "position": {"row": 0, "col": 0, "row_span": 1, "col_span": 1},
            "title": "月度销售趋势",
            "query": "SELECT month, amount FROM sales_monthly ORDER BY month",
            "echarts_option": {
                "xAxis": {"type": "category"},
                "yAxis": {"type": "value"},
                "series": [{"type": "line", "smooth": true}]
            }
        },
        {
            "id": "chart2",
            "position": {"row": 0, "col": 1, "row_span": 1, "col_span": 1},
            "title": "品类占比",
            "query": "SELECT category, amount FROM sales_category",
            "echarts_option": {
                "series": [{"type": "pie", "radius": "50%"}]
            }
        },
        {
            "id": "chart3",
            "position": {"row": 1, "col": 0, "row_span": 1, "col_span": 2},
            "title": "地区分布",
            "query": "SELECT province, amount FROM sales_region",
            "echarts_option": {
                "xAxis": {"type": "category"},
                "yAxis": {"type": "value"},
                "series": [{"type": "bar"}]
            }
        }
    ],
    "db_path": "workspace.db"
}
```

**生成仪表盘**：
```bash
python scripts/dashboard_generator.py --config outputs/configs/dashboard.json --output outputs/html/sales_dashboard.html
```

---

### 场景 11：URL 数据源导入

**触发条件**：用户需要从 API 接口导入数据。

**导入 JSON 数据**：
```bash
# 无认证
python scripts/data_importer.py url "https://api.example.com/data" --format json --table api_data

# Bearer Token 认证
python scripts/data_importer.py url "https://api.example.com/protected" --format json --table api_data --auth-type bearer --auth-token "your_token"

# Basic Auth 认证
python scripts/data_importer.py url "https://api.example.com/data" --format json --table api_data --auth-type basic --auth-user "username" --auth-password "password"
```

**刷新数据源**：
```bash
# 查看已导入的 URL 数据源
python scripts/data_importer.py list --db workspace.db

# 刷新指定表
python scripts/data_importer.py refresh api_data --db workspace.db
```

**JSON 嵌套处理**：
系统自动展平嵌套结构，如 `{"user": {"name": "张三"}}` 转换为列 `user_name`。

---

## 安装方式

将本 Skill 包导入到你的 Agent 平台的技能（Skills）库中即可：

1. 下载最新版本的 `echart-skill_*.zip` 压缩包并解压。
2. 根据你所使用的 Agent 平台：
   - **Trae**: 将解压后的文件夹放入 `~/.trae/skills/` 目录下。
   - **Claude Code / OpenClaw / WorkBuddy**: 查阅对应平台关于"如何安装自定义 Skill/Tool"的官方文档，将本目录挂载或配置入其上下文中。
3. **地图配置（可选）**：如果需要生成中国地图相关的图表，请设置环境变量 `BAIDU_AK`。你可以前往 [百度地图开放平台](https://lbsyun.baidu.com/index.php?title=jspopularGL/guide/getkey) 免费申请 AK。
   ```bash
   # 临时设置（当前终端会话有效）
   export BAIDU_AK=你的百度地图AK
   
   # 永久设置（推荐）- 根据你的 Shell 选择对应方式：
   # Zsh (macOS 默认)
   echo 'export BAIDU_AK=你的百度地图AK' >> ~/.zshrc
   source ~/.zshrc
   
   # Bash (Linux 常见)
   echo 'export BAIDU_AK=你的百度地图AK' >> ~/.bashrc
   source ~/.bashrc
   
   # 或安装依赖
   pip install -r requirements.txt
   ```

## 常见问题 (FAQ)

**Q: 为什么导入大 Excel 时有点慢？**
A: 本技能为了应对"脏数据"，会在底层调用 `openpyxl` 来遍历并解开所有的合并单元格（Merged Cells）。这种物理层面的解析比直接读取纯数据稍慢，但能保证数据的完整性和准确性。

**Q: 我发现 Agent 修改错数据了，怎么恢复？**
A: 本技能内置了"后悔药"机制。你可以直接对 Agent 说："刚才那一步算错了，撤销"，Agent 会由于没有覆盖原表，直接回退到上一个表版本。

**Q: 支持连接外部的 MySQL 或 PostgreSQL 吗？**
A: 本技能目前默认使用本地 SQLite 以追求开箱即用和零配置。如果需要连接外部数据库，你可以让 Agent 修改生成的连接字符串，架构上是完全支持的。

**Q: 如何从 API 接口导入数据？**
A: 使用 `data_importer.py url` 命令，指定 URL 和格式即可导入。支持 Basic Auth 和 Bearer Token 认证。导入后可使用 `refresh` 命令刷新数据。

**Q: 如何创建多图表仪表盘？**
A: 创建一个 JSON 配置文件，定义图表位置和配置，然后使用 `dashboard_generator.py` 生成即可。详见场景 10 示例。

## 功能清单

| 功能模块 | 脚本 | 说明 |
|---------|------|------|
| 数据导入 | `scripts/data_importer.py` | 支持 CSV/Excel/URL 导入，流式处理大文件 |
| 数据导出 | `scripts/data_exporter.py` | 导出为 CSV/Excel，支持 SQL 查询导出 |
| 图表生成 | `scripts/chart_generator.py` | 支持 ECharts 6.0 全量图表类型 |
| 仪表盘生成 | `scripts/dashboard_generator.py` | 多图表网格布局，单 HTML 输出 |
| 甘特图生成 | `scripts/gantt_chart.py` | 简化 API，支持任务数组输入 |
| 数据合并 | `scripts/data_merger.py` | 合并多个表格，支持导出和入库 |
| 数据清洗 | `scripts/data_cleaner.py` | 清洗、去重、标准化 |
| 本地服务 | `scripts/server.py` | 本地 HTTP 服务，预览图表 |
| 业务口径 | `scripts/metrics_manager.py` | 持久化业务规则和指标定义 |

## 更新日志

详见 [RELEASE_NOTE.md](./RELEASE_NOTE.md)
