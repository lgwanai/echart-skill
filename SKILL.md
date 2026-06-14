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
5. **Auto-start Server**: After generating ANY HTML chart/dashboard, ALWAYS ensure the local server is running and return the access URL. Use `python scripts/server_cli.py start` to auto-start if not running.

---

## Command System

> **双模式支持**: 本 Skill 同时支持**显性指令**和**模糊匹配**。当用户输入以 `/` 开头的指令时，直接执行对应操作；否则进行意图推断。

### 显性指令列表

| 指令 | 别名 | 功能 | 示例 |
|------|------|------|------|
| `/import` | `/i`, `/导入` | 数据导入 | `/import data.xlsx` |
| `/query` | `/q`, `/sql`, `/查询` | 执行 SQL 查询 | `/query SELECT * FROM sales LIMIT 10` |
| `/chart` | `/c`, `/图表`, `/viz` | 生成图表 | `/chart bar 销售额按类别` |
| `/chart-list` | `/cl`, `/图表列表` | 查看支持的图表类型 | `/chart-list` |
| `/export` | `/e`, `/导出` | 数据导出 | `/export result.csv --table sales` |
| `/tables` | `/t`, `/表`, `/结构` | 查看表结构 | `/tables sales` |
| `/history` | `/h`, `/历史` | 查看导入历史 | `/history --limit 20` |
| `/metrics` | `/m`, `/口径`, `/指标` | 指标管理 | `/metrics add 月活用户` |
| `/help` | `/?`, `/帮助` | 显示帮助 | `/help` |
| `/clean` | `/清理` | 清理旧数据 | `/clean --days 30` |
| `/poll` | `/轮询` | 轮询管理 | `/poll status` |
| `/dashboard` | `/db`, `/仪表盘` | 生成仪表盘 | `/dashboard config.txt` |
| `/start` | `/server`, `/启动服务` | 启动本地服务 | `/start` |
| `/stop` | `/停止服务` | 停止本地服务 | `/stop` |
| `/status` | `/状态` | 查看服务状态和链接 | `/status` |
| `/echart-update` | `/update`, `/更新` | 从 GitHub 拉取最新代码并备份旧文件 | `/echart-update` |
| `/analyze` | `/a`, `/分析` | 自动分析数据表，发现规律与异常 | `/analyze sales` |
| `/insight` | `/洞察` | 对指定维度生成深度洞察 | `/insight sales --dim region` |
| `/report` | `/r`, `/报告` | 一键生成专业分析报告 | `/report sales --template sales` |
| `/forecast` | `/f`, `/预测` | 时间序列预测 | `/forecast orders 订单日期 金额 --periods 6` |
| `/why` | `/w`, `/归因`, `/为什么` | 数据变化归因分析 | `/why orders 金额 订单日期 2024-01 2024-06` |
| `/context` | `/ctx`, `/会话` | 会话管理（开始/追问/历史/列表） | `/context start sales` |

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
│                ├── 预测关键词 ──→ Scenario 19 (趋势预测)          │
│                ├── 归因关键词 ──→ Scenario 20 (归因分析)          │
│                ├── 会话关键词 ──→ /context 子命令                  │
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

#### `/chart-list` - 查看支持的图表类型
```
/chart-list [类别]
/cl [类别]  # 别名
/图表列表 [类别]  # 中文别名

显示所有支持的图表类型及其简介。

参数:
  [类别]  可选，筛选特定类别：basic, statistical, hierarchical, 
          geographical, relation, 3d, time, professional

示例:
  /chart-list              # 显示所有图表
  /chart-list basic        # 显示基础图表
  /chart-list 3d           # 显示3D图表
  /cl                      # 别名
```

#### `/dashboard` - 仪表盘生成
```
/dashboard <描述> [--output <输出路径>]
/db <描述>  # 别名
/仪表盘 <描述>  # 中文别名

示例:
  # 自然语言描述（推荐）
  /dashboard 创建销售分析仪表盘，包含：各地区销售柱状图、产品类别饼图、月度趋势折线图、全国分布地图
  
  # 简化配置文件
  /dashboard outputs/configs/dashboard.json
  
  # 指定输出路径
  /dashboard 销售数据仪表盘，包含地区柱状图和类别饼图 --output outputs/html/sales.html

功能:
  - ✅ 自然语言描述自动解析
  - ✅ 智能布局算法自动排版
  - ✅ 简化 API，无需编写 SQL
  - ✅ 专业卡片式布局
  - ✅ 深色/浅色主题切换
  - ✅ 响应式设计
  - ✅ 自动刷新、导出 PDF
  - ✅ 图表搜索、单独下载
  - ✅ 智能数据洞察卡片（NEW v2.0 — 使用 --insights 启用）

选项:
  --insights                    启用数据洞察卡片（自动分析表数据并展示关键发现）
  --insights-dimensions, -d <列> 洞察分析的维度列（逗号分隔）
  --insights-date-column <列>    洞察分析的日期列（用于趋势/周期性检测）
  --insights-max <数量>          最大洞察卡片数（默认 6）

示例:
  # 基础仪表盘（不含洞察）
  /dashboard 创建销售分析仪表盘

  # 含洞察卡片的仪表盘
  /dashboard 销售分析仪表盘 --insights

  # 指定洞察分析的维度和日期列
  /dashboard 销售仪表盘 --insights --insights-dimensions region,category --insights-date-column order_date

洞察卡片功能:
  - 📈 自动发现 7 种洞察模式（趋势、异常、排名、构成、相关性、周期、变化）
  - 🔴🟠🟡⚪ 严重程度分级（严重/重要/中等/信息）
  - 🎯 每个卡片显示关键指标值和变化百分比
  - 🔍 悬停显示"点击深入分析"提示
  - 📊 自动推荐最合适的图表类型
  - 零额外配置 — 只需加 --insights 即可启用

支持图表类型:
  - bar (柱状图): group_by 参数
  - line (折线图): time_column 参数
  - pie (饼图): group_by 参数  
  - map (地图): geo_column 参数
  - scatter (散点图): x_column, y_column
  - radar (雷达图): dimensions
  - funnel (漏斗图): group_by
  - treemap (树图): group_by
  - sunburst (旭日图): hierarchy

自然语言描述示例:
  - 各地区销售柱状图 → 自动识别为 bar 类型，group_by='region'
  - 月度趋势折线图 → 自动识别为 line 类型，time_column='month'
  - 产品类别饼图 → 自动识别为 pie 类型，group_by='category'
  - 全国分布地图 → 自动识别为 map 类型，geo_column='province'
```

**支持的图表类型完整列表：**

| 类型 | 名称 | 类别 | 简介 |
|------|------|------|------|
| `bar` | 柱状图 | 基础 | 用于比较不同类别的数值大小，支持堆叠、分组 |
| `line` | 折线图 | 基础 | 展示数据随时间或类别的变化趋势，支持平滑曲线 |
| `pie` | 饼图 | 基础 | 展示各部分占整体的比例关系，支持环形图、玫瑰图 |
| `scatter` | 散点图 | 基础 | 展示两个变量之间的关系和分布，支持气泡效果 |
| `radar` | 雷达图 | 基础 | 多维度数据对比，适合性能评估、能力分析 |
| `area` | 面积图 | 基础 | 折线图的变体，强调累积变化趋势 |
| `boxplot` | 箱线图 | 统计 | 展示数据分布的五数概括（最小值、Q1、中位数、Q3、最大值） |
| `heatmap` | 热力图 | 统计 | 用颜色深浅表示数值大小，适合矩阵数据可视化 |
| `scattergl` | WebGL散点图 | 统计 | 高性能散点图，适合大数据量（百万级）渲染 |
| `effectScatter` | 涟漪散点图 | 统计 | 带动画效果的散点图，适合突出重点数据 |
| `lines` | 线图 | 统计 | 展示数据流向和轨迹，支持地图上的迁徙线 |
| `treemap` | 矩形树图 | 层级 | 用矩形面积展示层级数据的占比关系 |
| `sunburst` | 旭日图 | 层级 | 多层饼图，展示层级结构的占比关系 |
| `tree` | 树图 | 层级 | 展示层级结构的节点连接关系 |
| `sankey` | 桑基图 | 关系 | 展示数据流向和转化，适合漏斗分析、能量流 |
| `graph` | 关系图 | 关系 | 展示节点之间的网络关系，支持力导向布局 |
| `chord` | 和弦图 | 关系 | 展示节点之间的双向关系强度 |
| `funnel` | 漏斗图 | 专业 | 展示转化漏斗，适合分析各阶段流失率 |
| `gauge` | 仪表盘 | 专业 | 展示单个指标的达成进度，类似速度表 |
| `candlestick` | K线图 | 专业 | 展示股票等金融数据的开盘、收盘、最高、最低价 |
| `parallel` | 平行坐标图 | 专业 | 多维度数据并行展示，适合高维数据分析 |
| `calendar` | 日历图 | 时间 | 在日历上展示数据分布，适合活动打卡、出勤分析 |
| `themeRiver` | 主题河流图 | 时间 | 展示多个主题随时间的变化趋势和占比 |
| `map` | 地图 | 地理 | 展示地理区域数据分布，支持中国、世界地图 |
| `geo` | 地理坐标系 | 地理 | 地理坐标系组件，配合 scatter、lines 使用 |
| `bar3d` | 3D柱状图 | 3D | 三维柱状图，适合展示三维数据矩阵 |
| `line3d` | 3D折线图 | 3D | 三维空间中的折线图 |
| `scatter3d` | 3D散点图 | 3D | 三维空间中的散点图 |
| `surface` | 3D曲面图 | 3D | 展示三维曲面数据，适合科学计算可视化 |

**图表类型类别说明：**

| 类别 | 说明 | 适用场景 |
|------|------|----------|
| **基础** `basic` | 最常用的图表类型 | 数据比较、趋势分析、占比展示 |
| **统计** `statistical` | 用于数据分析的图表 | 数据分布、相关性分析、大规模数据 |
| **层级** `hierarchical` | 展示层级结构 | 组织架构、分类体系、占比层级 |
| **关系** `relation` | 展示节点关系 | 社交网络、流程分析、转化漏斗 |
| **地理** `geographical` | 地图相关可视化 | 区域销售、人口分布、物流轨迹 |
| **3D** `3d` | 三维可视化 | 科学计算、立体展示 |
| **时间** `time` | 时间维度图表 | 日历分析、时间趋势 |
| **专业** `professional` | 特定领域专用 | 金融分析、进度监控、指标展示 |

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

#### `/start` - 启动本地服务
```
/start [--port <端口>]
/server [--port <端口>]  # 别名
/启动服务 [--port <端口>]  # 中文别名

启动本地 HTTP 服务器以查看生成的图表。

参数:
  --port <端口>  可选，指定端口号（默认自动选择 8100-8200）

示例:
  /start              # 自动选择可用端口启动
  /start --port 8080  # 指定端口启动
  /server             # 别名
```

#### `/stop` - 停止本地服务
```
/stop
/停止服务  # 中文别名

停止正在运行的本地 HTTP 服务器。

示例:
  /stop    # 停止服务
```

#### `/status` - 查看服务状态
```
/status
/状态  # 中文别名

查看服务运行状态和所有可访问的图表链接。

显示内容:
  - 服务状态（运行中/已停止）
  - 运行端口
  - 启动时间
  - 运行时长
  - 可访问图表列表（带完整 URL）

示例:
   /status  # 查看当前状态和链接
```

#### `/echart-update` - 更新 Skill
```
/echart-update
/update  # 别名
/更新  # 中文别名

自动更新 echart-skill，支持首次安装和后续更新。

功能:
  - ✅ 自动检测：是 git 仓库则 pull，否则提示 clone
  - ✅ 更新前自动创建带日期的备份压缩包
  - ✅ 排除临时文件、数据库文件等
  - ✅ 备份文件保存在 backup/ 目录

首次安装:
  # macOS/Linux
  cd ~/.agents/skills  # 或你的 skill 目录
  git clone https://github.com/lgwanai/echart-skill.git

  # Windows (PowerShell)
  cd $env:USERPROFILE\.agents\skills
  git clone https://github.com/lgwanai/echart-skill.git

后续更新:
  /echart-update  # 自动 pull + 备份
  /update         # 别名
  /更新           # 中文别名

输出:
  📦 备份文件: backup/echart-skill_backup_20260524_120000.zip
  ✅ 更新成功
```

#### `/analyze` - 自动数据分析
```
/analyze <表名> [选项]
/a <表名>  # 别名
/分析 <表名>  # 中文别名

自动分析数据表，发现趋势、异常、排名、占比、相关性等规律。

选项:
  --dimensions, -d <列名列表>  指定分析维度（逗号分隔）
  --metric, -m <列名列表>      指定分析指标（逗号分隔）
  --date-column <列名>         指定时间列
  --top-n <数量>               Top-N 数量（默认 5）
  --quick                      快速扫描模式
  --format <text|json>         输出格式

示例:
  /analyze sales                           # 自动分析 sales 表
  /analyze orders --dimensions region,category --metric amount
  /analyze sales --date-column order_date  # 含时间序列分析
  /analyze sales --quick                   # 快速扫描
  /a sales                                 # 别名

洞察类型:
  - 📈 趋势分析: 上升/下降趋势，趋势加速/减速
  - ⚠️ 异常检测: Z-score 检测异常波动
  - 📊 排名分析: Top-N / Bottom-N 排名
  - 🥧 占比分析: 构成分布与集中度
  - 🔗 相关性: 指标间关联关系
  - 📅 季节性: 周期性规律检测
  - 📉 变化分析: 环比/同比变化
```

#### `/insight` - 深度洞察
```
/insight <表名> --dim <维度列> [选项]
/洞察 <表名> --dim <维度列>  # 中文别名

对指定维度生成深度洞察，适合追问"为什么"的场景。

示例:
  /insight sales --dim region          # 各地区深度分析
  /insight sales --dim product --metric amount,quantity
  /insight orders --dim channel --top-n 10
```

#### `/report` - 分析报告生成
```
/report <表名> [选项]
/r <表名>  # 别名
/报告 <表名>  # 中文别名

一键生成专业数据分析报告，支持 Markdown/HTML/JSON 格式。

选项:
  --title, -t <标题>           报告标题
  --template <模板名>           报告模板: general, sales, quick
  --format <markdown|html|json> 输出格式（默认 markdown）
  --output, -o <路径>          输出路径
  --quick                       快速报告模式

报告模板:
  - general: 通用数据分析报告（含摘要/概览/指标/维度/趋势/异常/建议）
  - sales:   销售分析报告（含销售概况/产品/渠道/区域/趋势）
  - quick:   快速分析摘要（核心发现/数据画像/关键洞察/行动建议）

示例:
  /report sales                                    # 生成通用报告(Markdown)
  /report sales --template sales --format html     # 销售报告(HTML)
  /report orders --quick --format markdown         # 快速摘要
  /r sales --title "Q1销售分析" --format html       # 指定标题
```

#### `/forecast` - 时间序列预测
```
/forecast <表名> <日期列> <指标列> [选项]
/f <表名> <日期列> <指标列>  # 别名
/预测 <表名> <日期列> <指标列>  # 中文别名

基于纯 Python 实现的时间序列预测，支持多种方法，零外部依赖（无需 sklearn/tensorflow）。

选项:
  --periods, -p <数量>        预测期数（默认 6）
  --method, -m <方法>         预测方法: moving_average(移动平均), exponential(指数平滑), linear_trend(线性趋势), ensemble(集成,默认)
  --granularity, -g <粒度>    时间粒度: day(日), week(周), month(月,默认), quarter(季), year(年)
  --filter <条件>             数据过滤条件（SQL WHERE 子句）
  --db <数据库路径>           数据库路径（默认 workspace.duckdb）
  --format <text|json>        输出格式

预测方法说明:
  - moving_average: 移动平均法 — 自适应窗口，适合稳定序列
  - exponential:    指数平滑法 — 含趋势检测，适合有趋势的序列
  - linear_trend:   线性回归法 — 给出 R² 置信度，适合线性趋势
  - ensemble:       集成方法 — 加权融合以上三种方法（推荐）

输出内容:
  - 历史数据摘要（最近 6 期）
  - 未来 N 期预测值
  - 预测区间（上下限 80% 置信区间）
  - 置信度评分 (0-1)
  - 趋势方向（上升/下降/平稳）及变化率

示例:
  /forecast orders 订单日期 金额 --periods 6                   # 默认集成预测
  /forecast orders 订单日期 金额 --method linear_trend -p 12  # 线性趋势预测12期
  /forecast sales order_date amount --granularity quarter    # 按季度预测
  /f orders 下单时间 数量 --periods 3 -m exponential         # 指数平滑预测3期
```

#### `/why` - 归因分析
```
/why <表名> <指标列> <日期列> <起始期> <终止期> [选项]
/w <表名> <指标列> <日期列> <起始期> <终止期>  # 别名
/归因 <表名> <指标列> <日期列> <起始期> <终止期>  # 中文别名
/为什么 <表名> <指标列> <日期列> <起始期> <终止期>  # 中文别名

分析指标变化的根本原因，将总变化分解到各维度的贡献值，自动推荐钻取路径。

选项:
  --dimensions, -d <维度列表>  分析维度，逗号分隔（默认自动检测前3个分类维度）
  --top-n <数量>               每个维度返回的 top 贡献项数（默认 8）
  --db <数据库路径>             数据库路径（默认 workspace.duckdb）
  --format <text|json>         输出格式

分析内容:
  - 总量变化（起始值 → 终止值，变化率）
  - 各维度 Top 驱动力排名（含贡献百分比）
  - 抵消效应检测（增长/下降维度分布）
  - 自动化钻取建议（下一步从哪里深入分析）

贡献度阈值:
  - 贡献度 ≥ 15% 标记为主要驱动力（📌）
  - 贡献度 < 15% 归为次要因素

示例:
  /why orders 金额 订单日期 2024-01 2024-06 -d 商品分类,渠道,支付方式
  /why sales amount order_date 2024-Q1 2024-Q2 --dimensions region,category
  /w orders 数量 日期 2025-01 2025-03
  /为什么 sales 销售额 下单日期 2024-01 2024-06 -d 省份
```

#### `/context` - 会话管理
```
/context <子命令> [参数]
/ctx <子命令>  # 别名
/会话 <子命令>  # 中文别名

管理分析会话状态，支持会话创建、追问解析、历史查看、会话列表等功能。

子命令:
  start <表名> [选项]    开始新的分析会话
  resolve <文本>         解析追问内容（"上个月呢？"等）
  history                查看当前会话的对话历史
  context                查看当前会话的上下文提示词
  list                   列出所有已保存的会话

start 选项:
  --db <路径>                   数据库路径（默认 workspace.duckdb）
  --dimensions, -d <维度列表>   分析维度，逗号分隔
  --metrics, -m <指标列表>      关注指标，逗号分隔
  --date-column <日期列>        日期列名
  --semantic-model, -s <模型>   关联的语义模型名

会话功能说明:
  - 会话持久化存储（SQLite），重启后保留上下文
  - 自动时间上下文检测（从表数据中推断日期范围）
  - 支持 10+ 种时间表达式解析（上个月/去年/Q1/最近N天...）
  - 意图检测：refine(细化)、compare(对比)、pivot(切换维度)、drill_down(深挖)、explain(归因)、predict(预测)

追问类型对照:
  | 类型 | 示例 | 系统行为 |
  |------|------|----------|
  | REFINE | "上个月呢？" | 解析时间引用，调整查询范围 |
  | COMPARE | "和去年同期比" | 检测同比/环比，生成对比查询 |
  | DRILL_DOWN | "深挖一下白酒" | 应用维度过滤器 |
  | EXPLAIN | "为什么下降了" | 触发归因分析（→ /why） |
  | PIVOT | "按渠道分析" | 切换分析维度 |
  | PREDICT | "预测下个月" | 触发趋势预测（→ /forecast） |

示例:
  /context start sales                                          # 开始分析 sales 表
  /context start orders --dimensions region,category --db workspace.duckdb
  /context resolve "上个月呢？"                                   # 解析追问
  /context resolve "和去年同期比" --session-id <id>              # 指定会话
  /context history                                              # 查看历史
  /context context                                              # 查看上下文
  /context list                                                 # 列出所有会话
  /ctx list                                                     # 别名
```

### 模糊匹配关键词

当用户输入不是显性指令时，通过关键词推断意图：

| 意图 | 触发关键词 | 执行 Scenario |
|------|-----------|---------------|
| 数据导入 | 上传、导入、import、load、打开文件、读取 | Scenario 1 |
| SQL 查询 | 查询、筛选、统计、分组、排序、select、group by | Scenario 2 |
| 图表生成 | 图表、可视化、画图、chart、plot、展示、可视化 | Scenario 4 + 自动启动服务 |
| 数据导出 | 导出、下载、export、保存、输出 | Scenario 6 |
| 表结构 | 表结构、字段、列、describe、schema | Scenario 10 |
| 导入历史 | 历史、导入记录、history | Scenario 10 |
| 指标管理 | 指标、口径、定义、metric | Scenario 8 |
| 服务管理 | 服务、服务器、启动、停止、server、start、stop | 直接执行 /start 或 /stop |
| Skill 更新 | 更新、拉取、update、pull、升级 | 执行 /echart-update |
| 自动分析 | 分析、洞察、发现、规律、趋势、异常、相关性、report、analyze | Scenario 16 |
| 报告生成 | 报告、总结、出报告、结论、写报告、生成报告 | Scenario 17 |
| 追问/继续 | 呢？、比呢？、刚才、上次、继续、深挖、为什么、换 | Scenario 18 |
| 趋势预测 | 预测、预估、趋势、forecast、预测未来、走向、接下来 | Scenario 19 |
| 归因分析 | 为什么、原因、驱动因素、归因、贡献、变化分析、why、explain | Scenario 20 |
| 会话管理 | 会话、上下文、context、session、对话历史、追问 | /context 子命令 |

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

#### 🎯 ECharts 图表生成 — 零模板，纯 .md 驱动

> ⛔ **每个 `.md` 是自包含图表配方——包含完整 JS 代码 + 数据替换点 + HTML 壳。**

```
用户请求 "/chart bar 销售额"
 ↓
Step 1: DuckDB 查询真实数据
   └─ SQL → 获取实际数据行
 ↓
Step 2: 查 references/examples/INDEX.md → 定位 {name}.md
   └─ 354 个自包含图表配方
 ↓
Step 3: 读 {name}.md → 提取 Complete Code
   └─ 官方 JS 代码（可直接运行）
 ↓
Step 4: 替换 data 数组为 DuckDB 真实数据
   └─ regex: data: [...] → data: [真实值]
 ↓
Step 5: 包裹 HTML 壳（echarts inline + div#main + script）
   └─ 见 .md 中的 ## HTML Shell 模板
 ↓
Step 6: 对照 docs/CHART_DEBUG_LOG.md 避坑（34 条）
 ↓
Step 7: validate_chart.py 硬校验（7 项）
   └─ python scripts/validate_chart.py <output.html>
 ↓
通过→返回用户 / 失败→修复→重试
```

**关键原则**：
- ❌ 不用 `build_template.py`（模板系统已废弃）
- ❌ 不用 `{{PLACEHOLDER}}`（占位符系统已废弃）
- ✅ 每个 `.md` = 完整的独立图表配方
- ✅ Agent 只需：DuckDB + `.md` 代码 + 数据替换 → HTML

### 🗺️ 生成模式决策树（MUST FOLLOW — 先判断模式，再执行）

```
用户图表需求
    │
    ├── 是单个图表？
    │   ├── 模板存在？(查 templates/INDEX.md)
    │   │   ├── YES → 🟢 模板模式（最快最可靠）
    │   │   │   1. 读取模板 HTML → 获取占位符列表
    │   │   │   2. 按模板 data 格式从 DuckDB 生成 JSON
    │   │   │   3. 填充占位符 → 输出
    │   │   │
    │   │   └── NO → 🟡 知识库模式（兜底）
    │   │       1. 查 knowledge/INDEX.md → 读知识片段
    │   │       2. 查 examples/INDEX.md → 读案例 main.js
    │   │       3. 知识 + 案例 → 生成完整 option
    │   │       4. 用 chart_generator.py 生成 HTML
    │   │
    │   └── 需要自定义系列？(custom series)
    │       └── 🟡 知识库模式 + custom/error-bar.html 模板
    │
    ├── 是多个图表组合？(dashboard / 混合布局)
    │   ├── 每个子图表有独立模板？
    │   │   └── YES → 🔵 组合模式
    │   │       1. 对每个子图表执行模板模式
    │   │       2. 用 grid 布局将多个图表放入一个 HTML
    │   │       3. 每个图表独立 init + setOption
    │   │       4. 所有 JS 内联到单个文件
    │   │
    │   └── 子图表类型复杂？→ 用 /dashboard 命令 + SimpleDashboard API
    │
    └── 是 Dashboard？（3+ 图表 + 交互）
        └── 🟣 Dashboard 模式
            1. 使用 SimpleDashboard API
            2. 自然语言描述 → 自动解析图表类型
            3. 自动布局 + 卡片式 UI
            4. 参考 Scenario 15
```

### 🟢 模板模式（优先使用）

当 `templates/INDEX.md` 中有匹配模板时，**必须优先使用模板模式**：

1. 用户请求 → 提取图表类型 + 特征词 → 查 `templates/INDEX.md` → 定位模板
2. 读模板 HTML 文件 → 获取 `{{占位符}}` 列表和 data 格式
3. 从 DuckDB 查询数据 → 按模板格式生成 JSON
4. 填充占位符 → `chart_generator.py` 内联 JS 库 → 输出

### 🔵 组合模式（多图表）

当用户需求=多个独立图表组合在一个页面时：

1. 拆解需求为 N 个子图表
2. 每个子图表独立走模板模式
3. 用多 grid 布局组装：
```html
<div id="chart1" style="width:50%;height:400px;float:left"></div>
<div id="chart2" style="width:50%;height:400px;float:left"></div>
<script>
var c1 = echarts.init(document.getElementById('chart1'));
c1.setOption({{OPTION1}});
var c2 = echarts.init(document.getElementById('chart2'));
c2.setOption({{OPTION2}});
</script>
```
4. 输出为单个 self-contained HTML

### 🟡 知识库模式（兜底 — 无模板时使用）

当 `templates/INDEX.md` 中**没有**匹配模板时（如用户需要 custom series、极特殊图表、或模板覆盖不到的变体），回退到 4 步工作流：

1. 查 `knowledge/INDEX.md` → 读知识片段
2. 查 `examples/INDEX.md` → 读案例 main.js
3. 知识 + 案例代码一起作为上下文 → 生成完整 echarts option
4. 通过 chart_generator.py 生成 HTML

### 🗺️ 检索决策树（知识库模式专用）

```
用户请求图表
    │
    ├── 图表是什么类型？
    │   ├── bar/line/pie/scatter → chart-types/0X-*.md
    │   └── candlestick/radar/gauge/funnel/sankey/treemap/sunburst/
    │       graph/tree/heatmap/parallel/boxplot/calendar/map/geo/
    │       pictorialBar/themeRiver/custom → 直接用案例代码作主参考
    │
    ├── 需要什么概念？
    │   ├── 数据绑定 → concepts/01-dataset.md
    │   ├── 颜色/大小映射 → concepts/02-visual-map.md
    │   ├── 数据筛选/排序 → concepts/03-data-transform.md
    │   ├── 样式定制 → concepts/04-style.md
    │   ├── 点击交互 → concepts/05-event.md
    │   ├── 坐标轴配置 → concepts/06-axis.md
    │   ├── 图例配置 → concepts/07-legend.md
    │   └── 容器/响应式 → concepts/08-chart-size.md
    │
    ├── 需要什么模式？
    │   ├── 渲染器选择 → patterns/01-canvas-vs-svg.md
    │   ├── 动画效果 → patterns/02-animation.md
    │   ├── 富文本标签 → patterns/03-rich-text.md
    │   ├── 异步数据加载 → patterns/04-dynamic-data.md
    │   ├── 窗口适配 → patterns/05-responsiveness.md
    │   ├── 用户数据安全 → patterns/06-security.md
    │   ├── 无障碍 → patterns/07-accessibility.md
    │   ├── SVG 底图 → patterns/08-svg-base-map.md
    │   ├── 拖拽交互 → patterns/09-drag-interaction.md
    │   └── 按需引入 → patterns/10-import-strategy.md
    │
    └── 案例匹配（必须做！）
        └── 查 examples/INDEX.md → 读 <匹配案例>/main.js
```

### 🗺️ 模板选择决策树（必须执行）

```
Step 2.5: 根据图表类型+特征 → 选择 HTML 模板

查询 references/templates/INDEX.md，按以下规则匹配：

1. 提取图表类型关键词 → 定位模板目录
   bar/柱状图 → templates/bar/
   line/折线图 → templates/line/
   pie/饼图 → templates/pie/
   ... (完整映射见 templates/INDEX.md)

2. 提取特征关键词 → 定位具体模板文件
   bar + "堆叠" → bar/stack.html
   bar + "横向" → bar/horizontal.html
   bar + "瀑布" → bar/waterfall.html
   bar + "动态/排序/竞赛" → bar/race.html
   bar + (其他) → bar/basic.html
   line + "面积" → line/basic.html (areaStyle:{})
   line + "阶梯" → line/basic.html (step:'end')
   line + "堆叠" → line/stack.html
   line + "XY/数值" → line/xy.html
   line + (其他) → line/basic.html
   pie + "环形" → pie/basic.html (radius:['40%','70%'])
   pie + "玫瑰" → pie/basic.html (roseType:'area')
   scatter + "气泡" → scatter/bubble.html
   scatter + "地图" → scatter/geo.html
   (完整特征匹配表见 templates/INDEX.md)

3. 读取模板文件 → 获取占位符列表
   模板中所有 {{VARIABLE}} 即需要生成的 data 字段
   模板头部注释说明 data 格式和示例

4. 根据模板要求的 data 格式 → 从 DuckDB 生成 JSON
   模板只定义数据注入点，不定义数据来源
   Agent 负责 SQL → JSON 转换
```

### 📂 文件路径速查

| 类别 | 路径 |
|------|------|
| 知识库索引 | `references/knowledge/INDEX.md` |
| 案例索引 | `references/knowledge/examples/INDEX.md` |
| 模板映射索引 | `references/templates/INDEX.md` |
| 图表配方（自包含）| `references/examples/<chart-name>.md` — 354 个，每个 = 完整 JS + 数据替换点 + HTML 壳 |
| 模板构建脚本 | `scripts/build_template.py` |
| 概念文件 | `references/knowledge/concepts/` |
| 图表类型文件 | `references/knowledge/chart-types/` |
| API 文件 | `references/knowledge/api/` |
| 模式文件 | `references/knowledge/patterns/` |
| 案例代码 | `<你的工作区>/echarts-examples/<案例名>/main.js` |

> ⚠️ **已废弃**：`references/prompts/` 目录中的旧 Prompt 模板已被上述知识库 + 案例索引方案取代。该目录保留仅用于向后兼容，不再作为图表生成的主要参考源。新图表生成必须使用 `references/knowledge/` + 案例代码。

---

#### 📋 图表配置生成（原有流程）

1. 执行上述 4 步工作流获取语法约束和参考代码。
2. Do NOT write custom Python scripts from scratch. We have a powerful template-based rendering engine. Use the built-in `scripts/chart_generator.py` script.
3. Formulate the SQL query that aggregates the data correctly.
4. Generate the `custom_js` and `echarts_option` based on the knowledge + examples.
5. Construct a JSON configuration file (save it in `outputs/configs/`) matching this structure:
   ```json
    {
        "db_path": "workspace.duckdb",
       "query": "SELECT category, SUM(value) as val FROM table GROUP BY category",
       "title": "Chart Title",
       "output_path": "<echart-skill路径>/outputs/html/output_chart.html",
       "echarts_option": { ... }, // Generated option from prompt
       "custom_js": "..." // Optional JS logic for complex data binding
   }
```
    *Note: Output files MUST be stored in the isolated `outputs/html/` directory.*
    

### 🔒 Single File 模式 — 硬性铁律

> ⛔ **绝对禁止使用任何外部 URL 引用！！所有 CSS、JS、字体、地图数据必须内联到单个 HTML 文件中。**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Single File 铁律                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ❌ 禁止: <script src="https://cdn..."></script>                 │
│  ❌ 禁止: <script src="echarts.min.js"></script>                 │
│  ❌ 禁止: <link rel="stylesheet" href="...">                     │
│  ❌ 禁止: <script src="./local-file.js"></script>                │
│  ❌ 禁止: @import url(...)                                       │
│  ❌ 禁止: $.get() fetch 远程 GeoJSON                             │
│                                                                 │
│  ✅ 必须: <script>/* echarts 完整库代码内联 */</script>          │
│  ✅ 必须: <style>/* 所有 CSS 样式内联 */</style>                 │
│  ✅ 必须: 地图数据由 generator 自动内联注入                       │
│  ✅ 必须: 输出为单个 .html 文件，双击浏览器即可打开              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**实现方式**：
- `chart_generator.py` 会自动将 `echarts.min.js`、地图 JS 等依赖内联注入到 HTML 中
- 生成 ECharts option 时，**不写任何 `<script src=...>` 或 `<link href=...>`**
- 地图数据（china.js, world.js 等）由 generator 自动处理内联，不在 option 中引用
- 百度地图 SDK 是唯一例外（必须远程加载），仅在用户配置了 `BAIDU_AK` 且使用 bmap 模式时才允许

### ⚠️ ECharts 关键规则
    **CRITICAL ECHARTS RULES**:
    1. **Pie on Map**: The ECharts `pie` series DOES NOT support `coordinateSystem: 'geo'`. If the user asks to display data on a map, you MUST use `scatter` or `effectScatter` series with bubble sizes representing the values. NEVER attempt to put a pie chart on a geo map directly.
    
    2. **Map Generation Priority (CRITICAL)**:
       - **Local Static Maps (First Choice)**: For China provinces (`"map": "china"`), World countries (`"map": "world"`), or Chinese provinces (`"map": "guangdong"`, `"map": "beijing"`), ALWAYS use local static map JS files directly. DO NOT use `$.get()` to fetch GeoJSON from remote URLs. DO NOT use `echarts.registerMap()` for these standard maps. Just set `"map": "china"` or `"map": "world"` in the series config - the generator will auto-inject the correct JS file.
       
       - **Example (CORRECT)**:
         ```json
         {
           "series": [{
             "type": "map",
             "map": "china",  // Directly use map name
             "roam": true,
             "data": [{"name": "北京", "value": 15000}]
           }]
         }
         ```
       
       - **Example (WRONG - DO NOT USE)**:
         ```javascript
         // ❌ DO NOT use $.get for local static maps
         $.get(ROOT_PATH + '/data/asset/geo/china.json', function(geoJSON) {
           echarts.registerMap('china', geoJSON);  // Unnecessary!
         });
         ```
       
       - **BMap Mode (Fallback)**: Use `"bmap"` mode only when local static maps don't cover the required granularity (e.g., city-level data without province map, street-level data, or specific foreign countries not in world.js). This requires `BAIDU_AK` environment variable.
    
    3. **Baidu AK Types**: If the user provides a Baidu Map AK, remember there are two types: 1) JavaScript API (Frontend) and 2) Geocoding API (Backend Python). If backend Python geocoding fails with "status 240", it means the AK is a Browser-type AK and lacks Backend Geocoding permissions. Fallback to hardcoded coordinates in JS or ask for a "Server-side" AK.
    
    4. **Gantt Chart**: Uses a dedicated simplified API (see Scenario 9) rather than the template-based approach. Use `scripts/gantt_chart.py` for timeline visualizations.
 7. Execute the command:
    ```bash
    python scripts/chart_generator.py --config outputs/configs/your_config.txt
    ```

 8. **[CRITICAL] Return Chart Access**: After generating the chart, check the server configuration:

    ```bash
    # Check config: is server enabled?
    python -c "from scripts.config_manager import get_config; print(get_config().server.enabled)"
    ```

    **If server is disabled (default)**:
    - The chart is a self-contained HTML file (all JS embedded inline).
    - Return the absolute file path directly:
    ```
    ✅ 图表已生成: /absolute/path/to/outputs/html/sales_chart.html
    📂 可在浏览器中直接打开: file:///absolute/path/to/outputs/html/sales_chart.html
    ```

    **If server is enabled** (user has set `server.enabled=true` in `echart_config.txt`):
    - Start or check the server:
      ```bash
      python scripts/server_cli.py status
      python scripts/server_cli.py start  # auto-starts if not running
      ```
    - Return the access URL:
    ```
    ✅ Chart generated: outputs/html/sales_chart.html
    📊 View chart: http://localhost:{port}/outputs/html/sales_chart.html
    ```
    - If server start fails, retry once. If still fails, fall back to showing the local file path.

    **IMPORTANT**: All generated HTML files are now **self-contained** — they embed the ECharts library and all map scripts inline, so they work offline without any server.

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

 2. **[CRITICAL] Auto-start Server**: After generating the Gantt chart, ensure server is running:
    ```bash
    python scripts/server_cli.py start  # Auto-starts if not running
    ```

 3. Return the access URL:
    ```
    ✅ Gantt chart generated: outputs/html/project_gantt.html
    📊 View chart: http://localhost:{port}/project_gantt.html
    ```

 4. Tasks support optional fields:
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

export_standalone_dashboard("dashboard_config.txt", "my_dashboard.html")
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
python scripts/chart_cli.py export-chart config.txt

# Specify output path
python scripts/chart_cli.py export-chart config.txt --output reports/sales.html

# Use dark theme
python scripts/chart_cli.py export-chart config.txt --theme dark
```

**Export Dashboard:**
```bash
python scripts/chart_cli.py export-dashboard dashboard_config.txt

# With custom output
python scripts/chart_cli.py export-dashboard dashboard_config.txt --output monthly_report.html --theme dark
```

**Export Gantt Chart:**
```bash
# Gantt chart config is a JSON array of tasks
python scripts/chart_cli.py export-gantt tasks.txt --title "项目进度"

# With output path
python scripts/chart_cli.py export-gantt tasks.txt --title "Project Timeline" --output timeline.html
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
- `<config>`: Config file path (`.txt`; complex chart payloads may use JSON content)
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
python scripts/chart_cli.py export-dashboard daily_dashboard.txt \
    --output "reports/report_$(date +%Y%m%d).html"
```

**Notes:**
- Exported HTML files work offline (ECharts library embedded)
- File size ~1.2MB per export (includes ECharts library)
- Chinese characters are preserved correctly
- Generated filename format: `{sanitized_title}_{YYYYMMDD_HHMMSS}.html`

### Scenario 13: External Database Connections
**Trigger**: User needs to query data from MySQL, PostgreSQL, or MongoDB databases.

**Action:**

**1. Configure Connections (db_connections.txt):**
```ini
[connections.mysql_prod]
type=mysql
host=localhost
port=3306
database=production
username=admin
password=${MYSQL_PASSWORD}

[connections.postgres_analytics]
type=postgresql
host=analytics-db.internal
database=analytics
username=reader
password=${PG_PASSWORD}

[connections.mongo_docs]
type=mongodb
connection_string=${MONGODB_URI}
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
- Support for MySQL, PostgreSQL (via SQLAlchemy), and MongoDB (via PyMongo)

**Notes:**
- Default connection timeout: 30 seconds (override with `--timeout`)
- MongoDB documents are flattened for tabular storage (nested fields become `parent_child`)
- Arrays in MongoDB are expanded to indexed fields (`skills_0`, `skills_1`)

### Scenario 15: Dashboard Generation (Simplified Natural Language)
**Trigger**: User needs to create multi-chart dashboards with natural language.

**Method 1: Natural Language Description (Recommended)**

Simply describe what you want in plain language:

```
/dashboard 创建销售分析仪表盘，包含：
- 各地区销售柱状图
- 产品类别饼图
- 月度趋势折线图
- 全国分布地图
```

**Method 2: Simplified Python API**

```python
from scripts.simple_dashboard import SimpleDashboard

# Create dashboard with simplified API
dashboard = SimpleDashboard(
    title="销售数据分析",
    db_path="workspace.duckdb"
)

# Add charts with simple descriptions
dashboard.add_chart("bar", "地区销售额", group_by="region")
dashboard.add_chart("pie", "品类占比", group_by="category")  
dashboard.add_chart("line", "月度趋势", time_column="month")
dashboard.add_chart("map", "全国分布", geo_column="province")

# Generate
dashboard.generate("outputs/html/dashboard.html")
```

**Method 3: Direct Text-to-Dashboard**

```python
from scripts.simple_dashboard import create_dashboard_from_text

create_dashboard_from_text(
    """
    创建销售分析仪表盘，包含：
    - 各地区销售柱状图
    - 产品类别饼图
    - 月度趋势折线图  
    - 全国分布地图
    """,
    db_path="workspace.duckdb",
    output_path="outputs/html/dashboard.html"
)
```

**Supported Chart Types in Simplified API:**

| Chart Type | Keyword | Required Parameters |
|-------------|---------|---------------------|
| Bar Chart | `"bar"` | `group_by` |
| Line Chart | `"line"` | `time_column` or `group_by` |
| Pie Chart | `"pie"` | `group_by` |
| Map Chart | `"map"` | `geo_column` (province/city) |
| Scatter | `"scatter"` | `x_column`, `y_column` |
| Radar | `"radar"` | `dimensions` |
| Funnel | `"funnel"` | `group_by` |
| Treemap | `"treemap"` | `group_by` |
| Sunburst | `"sunburst"` | `hierarchy` |

**Optional Parameters:**

```python
dashboard.add_chart(
    chart_type="bar",
    title="Top 10 产品",
    group_by="product",
    agg_column="sales",      # 聚合列（默认求和）
    top_n=10,                # Top N
    sort="desc",             # 排序方式
    filter="region='华东'"   # 筛选条件
)
```

**Auto-Layout Algorithm:**

The system automatically:
- Calculates optimal grid columns based on chart count
- Assigns chart positions intelligently
- Maps get 2x1 span, Pies can span vertically
- Balances layout to avoid gaps

**Dashboard Features:**
- ✅ **Professional Card-based Layout**: Modern UI with shadow and hover effects
- ✅ **Dark/Light Theme Toggle**: Press the theme button to switch themes
- ✅ **Responsive Design**: Auto-adjusts for mobile, tablet, and desktop
- ✅ **Interactive Charts**: Each chart supports zoom, pan, tooltip
- ✅ **Auto-refresh**: Configure auto-refresh interval (default: 30 seconds)
- ✅ **Export PDF**: Export entire dashboard as PDF file
- ✅ **Chart Search**: Filter charts by title
- ✅ **Download Charts**: Download individual charts as PNG images

**Example Use Cases:**

**E-commerce Dashboard:**
```
/dashboard 创建电商数据仪表盘，包含：
- 各渠道销售柱状图
- 产品类别饼图
- 日销售趋势折线图
- 全国订单分布地图
```

**Financial Dashboard:**
```
/dashboard 创建财务分析仪表盘，包含：
- 月度收入折线图
- 费用类别饼图
- 部门预算柱状图
- 季度对比雷达图
```

**Method 4: Advanced Configuration (Legacy)**

For complex dashboards requiring full control, use JSON config:

```json
{
    "title": "销售数据概览",
    "columns": 3,
    "row_height": 400,
    "gap": 24,
    "db_path": "workspace.duckdb",
    "charts": [
        {
            "id": "chart1",
            "position": {"row": 0, "col": 0, "col_span": 2, "row_span": 1},
            "title": "月度销售趋势",
            "query": "SELECT month, SUM(amount) as sales FROM sales GROUP BY month",
            "echarts_option": {
                "xAxis": {"type": "category"},
                "yAxis": {"type": "value"},
                "series": [{"type": "line", "smooth": true}]
            },
            "custom_js": "option.series[0].data = rawData.map(r => r.sales);"
        }
    ]
}
```

Generate:
```bash
python scripts/dashboard_generator.py --config config.txt --output dashboard.html
```
**Trigger**: User needs to automatically refresh data from HTTP APIs or databases on a schedule.

**Action:**

**1. Create Polling Configuration (polling_config.txt):**
```ini
[jobs.sales_api]
source_type=http
source_name=sales_api
interval_seconds=300
table_name=live_sales
http_config.url=https://api.example.com/sales
http_config.format=json
http_config.auth.type=bearer
http_config.auth.token=${API_TOKEN}

[jobs.production_db]
source_type=database
source_name=production_db
interval_seconds=600
table_name=live_orders
db_profile=mysql_prod
query=SELECT * FROM orders WHERE created_at > NOW() - INTERVAL 1 HOUR
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
- Database polling for MySQL, PostgreSQL, MongoDB
- Automatic DuckDB table updates
- Last refresh timestamp tracked in `_data_skill_meta`
- Manual refresh on-demand
- Error counting and status tracking

**Notes:**
- Minimum interval: 10 seconds
- Maximum interval: 86400 seconds (24 hours)
- Polling runs in background thread
- Tables are replaced on each poll (not appended)

### Scenario 16: Automated Data Analysis (NEW in v1.6)
**Trigger**: User wants to understand their data — discover patterns, anomalies, trends without manually writing SQL or picking charts.

**Action**:

1. **Run Analysis**: Use the Insight Engine to automatically analyze a table:
   ```bash
   # Full analysis
   python scripts/insight_engine.py analyze <table_name> --db workspace.duckdb

   # Quick scan
   python scripts/insight_engine.py analyze <table_name> --quick --db workspace.duckdb

   # With specific dimensions
   python scripts/insight_engine.py analyze <table_name> \
       --dimensions region,category --metric amount --date-column order_date
   ```

2. **Profile First**: If you need to understand the data structure:
   ```bash
   python scripts/insight_engine.py profile <table_name> --db workspace.duckdb
   ```

3. **Present Insights**: The engine returns structured insights with:
   - 📈 **Trend**: Direction & strength of change over time
   - ⚠️ **Anomaly**: Statistical outliers (Z-score method)
   - 📊 **Ranking**: Top-N / Bottom-N by dimension
   - 🥧 **Composition**: Distribution & concentration
   - 🔗 **Correlation**: Relationships between metrics
   - 📅 **Seasonality**: Periodic patterns
   - 📉 **Change**: Period-over-period comparison

4. **Insight Output Format**: Each insight includes:
   - Severity level (critical/high/medium/low/info)
   - Natural language description in Chinese
   - Supporting evidence (numbers, periods, percentages)
   - Recommended chart type
   - Related columns for follow-up analysis

**From Python API**:
```python
from scripts.insight_engine import InsightEngine

engine = InsightEngine("workspace.duckdb")
insights = engine.analyze("sales", date_column="order_date")
for ins in insights:
    print(f"{ins.severity.value}: {ins.title} — {ins.description}")
```

**Key Features**:
- Completely automated — no need to write SQL or specify chart types
- Data privacy preserved — all computation is local in DuckDB
- Chinese natural language output
- Insights ranked by importance (critical → info)
- Each insight suggests the best chart type for visualization
- Supports time-series, categorical, and cross-metric analysis

### Scenario 17: Analysis Report Generation (NEW in v1.6)
**Trigger**: User wants a professional analysis report, not just individual charts or insights.

**Action**:

1. **Generate Report**:
   ```bash
   # Quick report (Markdown)
   python scripts/report_engine.py <table_name> --quick --format markdown

   # Full report with template
   python scripts/report_engine.py <table_name> --template sales --format html

   # Custom title and output
   python scripts/report_engine.py <table_name> \
       --title "销售数据分析报告" --template general --format html -o reports/sales_analysis.html
   ```

2. **Available Templates**:
   - `general` — 8-section comprehensive report (summary, overview, metrics, dimensions, trends, anomalies, correlation, recommendations)
   - `sales` — Sales-specific report (overview, product, channel, region, trend, recommendations)
   - `quick` — 4-section brief (key findings, profile, insights, actions)

3. **Output Formats**:
   - `markdown` — Clean markdown, ideal for embedding in AI responses
   - `html` — Styled HTML with dark/light theme support, ready to share
   - `json` — Structured JSON for programmatic consumption

4. **Report Content**: Each report includes:
   - Executive summary with key findings
   - Data overview table with column profiles
   - KPI statistics (mean, median, min, max, std)
   - Dimension analysis (rankings + compositions)
   - Trend analysis with direction and strength
   - Anomaly detection results
   - Correlation analysis
   - Actionable recommendations based on findings

**From Python API**:
```python
from scripts.report_engine import ReportEngine

engine = ReportEngine("workspace.duckdb")
path = engine.generate(
    table="sales",
    title="销售数据分析报告",
    template="sales",
    output_format="html",
)
print(f"Report: {path}")

# Quick mode for fast summaries
path = engine.quick_report("sales", output_format="markdown")
```

**Tips for Best Results**:
- Ensure table has proper column types (dates as DATE/TIMESTAMP, numbers as INT/DOUBLE)
- For time-series insights, specify a date column
- Use the `sales` template when table contains revenue, product, channel data
- Reports work offline — all analysis is local, no data leaves the machine
- Combine with `/chart` or `/dashboard` to add visualizations to the report

**Interaction Flow**:
```
User: /analyze sales
Agent: [Runs automated analysis, returns 26 insights with severity rankings]
       🔴 Critical: 单价环比增长113.9%
       🟠 High: 数量季节性波动59%
       🟡 Medium: 前2个渠道合计占69.1%
       ...

User: /report sales --template sales --format html
Agent: [Generates professional HTML report with all insights, charts recommendations]
       ✅ Report: outputs/reports/sales_sales_20260613_140000.html
```

**Integration with existing commands**:
- Use `/analyze` to discover what's interesting → Use `/chart` to visualize key findings
- Use `/report` for comprehensive analysis → Use `/dashboard` for interactive monitoring
- Use `/insight` to drill into specific dimensions found by `/analyze`

### Scenario 18: Contextual Follow-up (NEW in v1.7)
**Trigger**: User asks a follow-up question referencing previous analysis — "上个月呢?", "和去年同期比呢?", "深挖一下广东", "为什么下降了".

**Action**:

1. **Detect follow-up intent**: The Context Manager automatically determines if the user is starting a new topic or continuing:
   ```bash
   python scripts/context_manager.py resolve "上个月呢？"
   # Output: intent=FOLLOW_UP, follow_up=REFINE, time=2026-05-01~2026-05-31
   ```

2. **Start a session** (new analysis):
   ```bash
   python scripts/context_manager.py start orders --db workspace.duckdb
   ```

3. **View session context** for prompt injection:
   ```bash
   python scripts/context_manager.py context
   ```

**Supported Follow-up Types**:
| Type | Example | System Action |
|------|---------|--------------|
| REFINE | "上个月呢？" | Resolve time reference, re-run with adjusted time range |
| COMPARE | "和去年同期比" | Detect YoY/MoM, generate comparison query |
| DRILL_DOWN | "深挖一下白酒" | Apply dimension filter, zoom in |
| EXPLAIN | "为什么下降了" | Trigger attribution/root cause analysis |
| PIVOT | "按渠道分析" | Switch dimension, re-aggregate |

**From Python API**:
```python
from scripts.context_manager import ContextManager

ctx = ContextManager()
session = ctx.start_session("sales", dimensions=["region", "category"])

# Record a turn
ctx.record_turn(session, "查看各地区销售额",
                sql="SELECT region, SUM(amount) FROM sales GROUP BY region")

# Resolve follow-up
result = ctx.resolve("上个月呢？", session)
# result["time_range"] = {"start_date": "2026-05-01", "end_date": "2026-05-31", ...}
# result["is_follow_up"] = True
# result["context_prompt"] = "..."  # For LLM injection
```

**Key Features**:
- Session persistence across restarts (SQLite-backed)
- Automatic time context from table profiling
- 10+ time reference patterns (上个月/去年/Q1/最近N天...)
- Intent detection: refine, compare, pivot, drill-down, explain
- Generates prompt context for LLM agents
- Session history with query/SQL/chart tracking

### Scenario 19: Time-Series Forecasting (NEW in v2.0)
**Trigger**: User wants to predict future trends — "预测下季度销售", "接下来6个月的趋势", "预估明年的收入".

**Action**:

1. **Run Forecast**:
   ```bash
   # Basic ensemble forecast (recommended)
   python scripts/forecast_engine.py <table> <date_column> <metric> --periods 6

   # With specific method
   python scripts/forecast_engine.py sales order_date amount --method linear_trend -p 12

   # JSON output for programmatic use
   python scripts/forecast_engine.py sales order_date amount --format json -p 6
   ```

2. **Forecast Methods**:
   | Method | Best For | Confidence Indicator |
   |--------|----------|---------------------|
   | `ensemble` | Most cases (default) | Weighted average of all methods |
   | `moving_average` | Stable, non-trending data | Low CV (coefficient of variation) |
   | `exponential` | Data with trend/seasonality | Trend consistency |
   | `linear_trend` | Strong linear patterns | R² score |

3. **Output Includes**:
   - Historical values (last 6 periods shown)
   - Forecast values with upper/lower bounds (80% CI)
   - Trend direction (上升/下降/平稳) and strength (% per period)
   - Overall confidence score (0-1)

4. **Auto-Visualization**: After generating a forecast, ALWAYS suggest creating a line chart:
   ```
   /chart line 历史趋势与预测 --table <table>
   ```
   Or generate a forecast-specific chart that overlays historical + predicted values with confidence bands.

**From Python API**:
```python
from scripts.forecast_engine import ForecastEngine, ForecastMethod

engine = ForecastEngine("workspace.duckdb")

# Quick forecast
result = engine.quick_forecast("sales", "order_date", "amount", periods=3)
print(f"Trend: {result.trend_direction} ({result.trend_strength_pct:+.1f}%/period)")

# Detailed forecast with specific method
result = engine.forecast(
    "sales", "order_date", "amount",
    periods=12,
    method=ForecastMethod.EXPONENTIAL,
    granularity="month",
)

# Access results
for fp in result.forecast_points:
    print(f"{fp.period}: {fp.value:.1f} [{fp.lower_bound:.1f} - {fp.upper_bound:.1f}]")

# Export as dict
data = result.to_dict()  # Includes historical + forecast arrays
```

**Tips for Best Results**:
- Ensure the date column is properly typed (DATE/TIMESTAMP) for accurate period generation
- Use `--granularity quarter` for quarterly forecasting, `--granularity year` for annual
- The `ensemble` method is recommended for most cases — it blends all 3 methods
- Data with fewer than 4 periods will raise an error — ensure sufficient history
- Combine with `/chart line` for visual trend display
- Use `/why` to understand what drives the trend direction

**Interaction Flow**:
```
User: 预测接下来6个月的销售趋势
Agent: [Runs forecast_engine.py on sales table]
       📈 预测结果: amount
       方法: ensemble | 置信度: 85%
       趋势: up (+3.2%/期)
       
       历史数据 (12 期):
       2024-01           12,400
       ...
       
       预测 (6 期):
       期数         预测值        下限        上限
       2025-01      18,500     15,200     21,800
       ...
       
       💡 建议使用 /chart line 生成趋势图查看预测区间

User: /chart line 过去12个月销售额趋势及未来6个月预测
Agent: [Generates line chart with historical + forecast + confidence bands]
       ✅ Chart: outputs/charts/sales_trend_forecast_*.html
```

### Scenario 20: Attribution Analysis (NEW in v2.0)
**Trigger**: User wants to understand why a metric changed — "为什么销售额下降了", "广东的增长贡献了多少", "分析一下上个月的变化原因".

Note: When user asks "为什么" as a follow-up to an existing analysis session, the Context Manager (Scenario 18) automatically detects this as EXPLAIN intent and may resolve time references. Use attribution for both fresh analysis and as the EXPLAIN action in follow-up flows.

**Action**:

1. **Run Attribution Analysis**:
   ```bash
   # With explicit dimensions
   python scripts/attribution_engine.py <table> <metric> <date_column> <before> <after> \
       --dimensions 商品分类,渠道,支付方式

   # Auto-detect dimensions (uses first 3 category columns)
   python scripts/attribution_engine.py sales amount order_date 2024-01 2024-06

   # JSON output
   python scripts/attribution_engine.py sales amount order_date 2024-01 2024-06 \
       -d region,category --format json
   ```

2. **Period Format**: Use YYYY-MM for month-level analysis (e.g., `2024-01`, `2024-06`).

3. **Output Structure**:
   - **总量变化**: Total before → after, absolute change, percentage change
   - **主要驱动力**: Top contributors sorted by contribution %, with 📌 markers for ≥15% contribution
   - **抵消效应检测**: When some dimensions go up while others go down
   - **钻取建议**: Human-readable recommendations for further analysis

4. **Auto-Visualization**: After attribution, suggest:
   - `/chart bar 各维度变化贡献度` — waterfall/bar chart showing contribution by dimension
   - `/chart pie 各维度占比变化` — compare before vs after pie charts

**From Python API**:
```python
from scripts.attribution_engine import AttributionEngine

engine = AttributionEngine("workspace.duckdb")

# Detailed analysis
result = engine.explain_change(
    "sales", "amount", "order_date",
    "2024-01", "2024-06",
    dimensions=["region", "category", "channel"],
    top_n=8,
)

print(f"Change: {result.total_change_pct:+.1f}%")
print(f"Direction: {result.change_direction}")

for c in result.top_drivers:
    print(f"  {c.dimension}「{c.value}」: {c.change:+.1f} ({c.contribution_pct:+.1f}%)")

for rec in result.drill_recommendations:
    print(f"  💡 {rec}")

# Quick explain with auto-detected dimensions
result = engine.quick_explain("sales", "amount", "order_date", "2024-01", "2024-06")

# Export as dict
data = result.to_dict()
```

**Tips for Best Results**:
- Choose 2-4 meaningful dimensions for best insights (too many dilutes the analysis)
- Compare periods of similar length (e.g., Jan vs Jun, not Jan 2024 vs Jan 2025)
- Use month-level granularity for period format (YYYY-MM)
- Combine with `/analyze` to discover which dimensions are most important
- Combine with `/forecast` to understand if the change will continue
- Primary drivers are those with ≥15% absolute contribution

**Interaction Flow**:
```
User: /why orders 金额 订单日期 2024-01 2024-06 -d 商品分类,渠道
Agent: [Runs attribution_engine.py]
       🔍 归因分析: 金额
       2024-01 → 2024-06
       变化: 125000.0 → 158000.0 (+26.4%)
       
       📌 主要驱动力:
         商品分类「电子」: +22,500 (+19.8%)
         渠道「线上」: +15,800 (+13.9%)
       
       ⚖️ 存在抵消效应：3个维度增长、2个维度下降，建议分别分析。
       
       💡 建议:
         🔍 主要增长驱动力是商品分类维度的「电子」...
         📊 建议深挖该维度的明细数据。

User: 深挖一下电子产品
Agent: [Uses Context Manager to drill down: filter by 商品分类=电子]
       [Re-runs analysis with the filter applied]
```
