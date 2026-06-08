# Echart Skill v1.5.0

专门为 AI Agent 设计的本地数据分析与处理技能包（Skill），旨在解决日常办公场景下的高频、复杂数据分析任务。

## 项目亮点

- 🛡️ **绝对安全的数据隐私**：本技能要求 Agent 在本地存储数据（DuckDB），并在本地生成代码进行解析和计算。数据绝不出域，最大程度保障企业隐私。
- 📊 **27 种图表 + 356 官方案例**：内置完整 ECharts 知识库和 **356 个官方案例索引**，覆盖 **27 种图表类型**（含 3D、地理、关系图、桑基图等），每个案例的 `main.js` 在生成代码时作为实时参考，确保图表配置准确可用。
- 🧩 **自包含单文件 HTML**：生成的图表为完全自包含的单一 HTML 文件，ECharts 库和所有地图脚本均内联嵌入，离线可用，不受服务端口变化影响。
- ⚙️ **灵活的服务配置**：本地预览服务默认为关闭状态；可通过 `echart_config.txt` 配置启用、自定义输出目录、百度地图 AK 等。
- 🗺️ **智能地图名称标准化**：自动将数据中的「北京市」「广东省」等全称规范化为地图所需的「北京」「广东」，确保地图渲染一次成功。
- 🤖 **Dashboard 自然语言生成**：一句话描述即生成专业仪表盘——"创建销售分析仪表盘，包含地区柱状图、品类饼图、趋势折线图、分布地图"。
- 🎨 **专业 Dashboard UI/UX**：9 大交互功能（主题切换、导出 PDF、自动刷新、图表搜索），响应式卡片布局，深色/浅色主题。
- 🗺️ **三层级地图架构**：省份→城市→区县，优先静态本地地图（34 省份 + 全部城市），精细维度自动降级百度地图。
- 🤝 **广泛兼容性**：支持 **OpenClaw, Claude Code, WorkBuddy, OpenCode, Trae** 等主流 Agent 平台。
- ⚡ **强大的"脏表"处理能力**：智能识别复杂表头，自动打平合并单元格，流式处理超大文件。
- 💻 **15+ 显性指令**：`/import`、`/query`、`/chart`、`/dashboard`、`/export` 等，兼顾精准指令与自然语言。
- 🔗 **外部数据库**：MySQL、PostgreSQL、MongoDB 查询与导入。
- 🔄 **数据轮询**：定时从 HTTP API 或数据库自动刷新，适合实时监控。
- 🪟 **Windows 无感后台服务**：Windows 平台服务进程完全静默运行，无命令行窗口弹出。

---

## 快速开始

### 环境要求

- Python 3.10+
- 支持的操作系统：Windows、macOS、Linux

### 安装步骤

1. **下载并解压 Skill 包**

   **macOS / Linux:**
   ```bash
   unzip echart-skill_*.zip -d ~/skills/
   cd ~/skills/echart-skill
   ```

   **Windows (PowerShell):**
   ```powershell
   Expand-Archive echart-skill_*.zip -DestinationPath $env:USERPROFILE\skills\
   cd $env:USERPROFILE\skills\echart-skill
   ```

2. **安装 Python 依赖**

   > 💡 **网络不佳？** 如果发布包已包含 `wheels/` 目录，直接使用下方的离线安装命令，无需联网下载。

   **在线安装（默认）：**
   ```bash
   # 完整安装（核心 + 可选依赖，约 100 MB）
   pip install -r requirements.txt

   # 或仅核心依赖（约 40 MB，覆盖 90% 场景）
   pip install -r requirements-core.txt
   ```

   **离线安装（无需网络）：**
   ```bash
   # macOS / Linux
   bash scripts/install.sh --offline

   # Windows
   scripts\install.bat --offline

   # 也可以只装核心依赖（更小更快）
   bash scripts/install.sh --offline --core-only
   ```

   **依赖说明：**

   | 文件 | 内容 | 大小 | 何时需要 |
   |------|------|------|----------|
   | `requirements-core.txt` | DuckDB, pandas, openpyxl 等 | ~40 MB | 总是需要 |
   | `requirements-optional.txt` | MySQL/PostgreSQL/MongoDB 驱动、轮询、测试 | ~60 MB | 连接外部数据库时 |

3. **导入到你的 Agent 平台**

   根据你使用的 Agent 平台，选择对应的安装方式：

   #### Claude Code / OpenClaw

   **macOS / Linux:**
   ```bash
   # 创建符号链接（推荐）
   ln -s ~/skills/echart-skill ~/.claude/skills/echart-skill

   # 或直接复制
   cp -r ~/skills/echart-skill ~/.claude/skills/
   ```

   **Windows (PowerShell):**
   ```powershell
   # 复制到 Claude Code skills 目录
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills"
   Copy-Item -Recurse "$env:USERPROFILE\skills\echart-skill" "$env:USERPROFILE\.claude\skills\"
   ```

   在项目根目录创建 `CLAUDE.md`：

   ```markdown
   # 项目说明

   @~/.claude/skills/echart-skill/SKILL.md
   ```

   #### Trae / WorkBuddy

   ```bash
   cp -r ~/skills/echart-skill ~/.trae/skills/
   # 或
   cp -r ~/skills/echart-skill ~/.workbuddy/skills/
   ```

   **Windows:**
   ```powershell
   Copy-Item -Recurse "$env:USERPROFILE\skills\echart-skill" "$env:USERPROFILE\.trae\skills\"
   Copy-Item -Recurse "$env:USERPROFILE\skills\echart-skill" "$env:USERPROFILE\.workbuddy\skills\"
   ```

4. **配置百度地图 AK（可选）**

   如需生成精细维度的地图（区县、街道），需配置百度地图 AK：

   **macOS / Linux:**
   ```bash
   echo 'export BAIDU_AK=你的百度地图AK' >> ~/.zshrc
   source ~/.zshrc
   ```

   **Windows:**
   ```cmd
   setx BAIDU_AK "你的百度地图AK"
   ```

   免费申请地址：[百度地图开放平台](https://lbsyun.baidu.com/index.php?title=jspopularGL/guide/getkey)

---

## ECharts 图表生成工作流 ⛔ 硬性约束

### 🎯 三级生成策略

| 模式 | 触发条件 | 可靠度 | 说明 |
|------|---------|--------|------|
| 🟢 **模板模式** | 41 个模板覆盖了需求 | ★★★★★ | 只需生成 data JSON，零语法错误 |
| 🔵 **组合模式** | 多图表拼装到单页 | ★★★★★ | 多个模板 + grid 布局组装 |
| 🟡 **知识库兜底** | 模板覆盖不到的需求 | ★★★★ | 知识片段 + 356 案例代码参考 |

### 🟢 模板模式（优先 — 27 种图表 × 41 个模板）

```
用户请求 → 查 templates/INDEX.md → 定位模板 → 读占位符 → 生成 data JSON → build_template.py → 输出
```

**Agent 只需生成 data JSON，不需要写任何 ECharts option 代码：**
- 模板 = 完整 HTML + 预配置的 option 结构 + `{{ECHARTS_INLINE}}` 标记
- 占位符 = `{{TITLE}}`, `{{DATA}}`, `{{CATEGORIES}}`, `{{VALUES}}` 等
- data JSON 格式由模板头部注释定义

**模板 JS 内联机制：**

| 标记 | 注入内容 | 覆盖 |
|------|---------|------|
| `<!-- {{ECHARTS_INLINE}} -->` | echarts.min.js (1.1MB) | 全部 41 个模板 |
| `<!-- {{MAP_INLINE}} -->` | china.js / guangdong.js / world.js 等 | 5 个地图模板，自动检测 MAP_NAME |
| `<!-- {{GL_INLINE}} -->` | echarts-gl.min.js (625KB) | 5 个 3D 模板 |

```bash
# 生成自包含 HTML：
python scripts/build_template.py references/templates/bar/basic.html \
  -d data.json -o outputs/html/chart.html
# 输出：单个 .html 文件，双击浏览器即可打开，零外部依赖
```

### 🔵 组合模式

```
多个独立图表 → 各自走模板模式 → grid 布局组装 → 单 HTML 输出
```

### 🟡 知识库兜底（无模板时）

```
Step 1: 查 references/knowledge/INDEX.md → 定位知识文件
Step 2: 读知识片段（concepts/chart-types/api/patterns）→ 语法约束
Step 3: 读 356 案例 main.js → 真值参考
Step 4: 知识 + 案例一起提交 → 生成完整 option
```

### 项目结构

```
references/
├── templates/              # 41 个 HTML 模板（优先使用）
│   ├── INDEX.md            # 模板映射决策表
│   ├── bar/  5 个模板      # basic, stack, horizontal, waterfall, race
│   ├── line/  3 个模板     # basic, stack, xy
│   ├── pie/  1 个模板      # basic (含 doughnut/rose 变体)
│   ├── scatter/  3 个模板  # basic, bubble, geo
│   ├── 3d/  5 个模板       # bar3d, scatter3d, surface, globe, lines3d
│   └── ...  22 个更多模板  # 覆盖所有 27 种图表类型
├── knowledge/              # 知识库（兜底使用）
│   ├── INDEX.md            # 主索引
│   ├── concepts/  8 个     # 核心概念
│   ├── chart-types/  4 个  # 图表类型语法指南
│   ├── api/  6 个          # API 参考
│   ├── patterns/  10 个    # 最佳实践
│   └── examples/INDEX.md   # 356 案例索引
└── prompts/                # ⚠️ 已废弃
```

---

## 核心功能与使用案例

### 案例一：数据导入与自动清洗

**场景**：上传销售数据 Excel，自动识别并导入

**操作**：

```bash
# 方式1：使用显性指令
/import sales_2024.xlsx

# 方式2：自然语言
请帮我导入 sales_2024.xlsx 文件
```

**系统自动执行**：

1. 计算文件 MD5，跳过重复导入
2. 智能识别表头，处理合并单元格
3. 创建标准化表名（如 `sales_2024`）
4. 记录导入元数据（文件路径、行数、列数、时间戳）

**验证导入结果**：

```bash
# 查看所有表
/tables

# 查看表结构
/tables sales_2024

# 查看前几行数据
/query SELECT * FROM sales_2024 LIMIT 5
```

---

### 案例二：SQL 查询与数据分析

**场景**：分析各地区销售情况

**操作**：

```bash
# 简单查询
/query SELECT * FROM sales_2024 WHERE amount > 10000

# 聚合分析
/query SELECT region, SUM(amount) as total, COUNT(*) as orders 
       FROM sales_2024 
       GROUP BY region 
       ORDER BY total DESC

# 多表关联
/query SELECT a.product, a.sales, b.inventory
       FROM sales_2024 a
       JOIN inventory_2024 b ON a.product_id = b.product_id
       WHERE a.region = '华东'
```

**结果处理**：

- 查询结果直接显示在对话中
- 可以继续追问或要求可视化
- 可以导出为 CSV/Excel

---

### 案例三：单图表生成

**场景**：生成各类统计图表

#### 基础图表

```bash
# 柱状图
/chart bar 各产品销售额对比

# 折线图（带趋势）
/chart line 月度销售趋势 --smooth

# 饼图
/chart pie 各地区销售占比

# 散点图
/chart scatter 价格与销量关系分析

# 雷达图
/chart radar 各产品维度评分对比
```

#### 高级图表

```bash
# 桑基图（流程转化）
/chart sankey 用户购买路径转化分析

# 旭日图（层级占比）
/chart sunburst 产品类别层级占比

# 漏斗图（转化率）
/chart funnel 销售漏斗各阶段转化率

# 热力图（矩阵数据）
/chart heatmap 用户活跃时段分布

# 关系图（网络关系）
/chart graph 产品关联购买关系图
```

#### 地图图表（三层级架构）

```bash
# 省份级别 - 使用 china.js
/chart map 中国各省销售分布

# 城市级别 - 使用省份 JS（如 guangdong.js）
/chart map 广东省各城市人口分布

# 区县街道 - 使用百度地图 API
/chart bmap 广州市天河区门店分布
```

**地图使用规则**：

| 层级 | 数据示例 | 使用方式 | 地图文件 |
|------|---------|---------|---------|
| 省份 | 北京、上海、广东 | `"map": "china"` | `china.js` |
| 城市 | 广州市、深圳市、东莞市 | `"map": "guangdong"` | `guangdong.js` |
| 区县 | 天河区、南山区 | `"bmap": {...}` | 百度地图 API |

#### 3D 图表

```bash
# 3D 柱状图
/chart bar3d 产品三维销量矩阵

# 3D 曲面图
/chart surface 函数曲面可视化

# 3D 散点图
/chart scatter3d 三维空间数据分布
```

---

### 案例四：专业 Dashboard 生成（自然语言）

**场景**：用自然语言快速生成多图表仪表盘

#### 方法一：自然语言描述（推荐）

最简单的方式，直接描述想要的图表：

```bash
/dashboard 创建销售分析仪表盘，包含：
- 各地区销售柱状图
- 产品类别饼图
- 月度趋势折线图
- 全国分布地图
```

系统自动完成：
1. 解析图表类型和需求
2. 自动生成 SQL 查询
3. 智能布局排版
4. 生成专业仪表盘

#### 方法二：简化 API（Python）

```python
from scripts.simple_dashboard import SimpleDashboard

# 创建仪表盘
dashboard = SimpleDashboard(
    title="销售数据分析",
    db_path="workspace.duckdb"
)

# 添加图表（一行代码一个图表）
dashboard.add_chart("bar", "地区销售额", group_by="region")
dashboard.add_chart("pie", "品类占比", group_by="category")
dashboard.add_chart("line", "月度趋势", time_column="month")
dashboard.add_chart("map", "全国分布", geo_column="province")

# 生成
dashboard.generate("outputs/html/dashboard.html")
```

#### 方法三：一行代码生成

```python
from scripts.simple_dashboard import create_dashboard_from_text

create_dashboard_from_text(
    """
    创建电商数据仪表盘，包含：
    - 各渠道销售柱状图
    - 产品类别饼图
    - 日销售趋势折线图
    - 全国订单分布地图
    """,
    output_path="outputs/html/dashboard.html"
)
```

#### 支持的图表类型

| 图表类型 | 关键词 | 必需参数 | 示例 |
|---------|--------|---------|------|
| 柱状图 | `"bar"` | `group_by` | 各地区销售柱状图 |
| 折线图 | `"line"` | `time_column` | 月度趋势折线图 |
| 饼图 | `"pie"` | `group_by` | 产品类别饼图 |
| 地图 | `"map"` | `geo_column` | 全国分布地图 |
| 散点图 | `"scatter"` | `x_column`, `y_column` | 价格销量散点图 |
| 雷达图 | `"radar"` | `dimensions` | 产品评分雷达图 |
| 漏斗图 | `"funnel"` | `group_by` | 销售漏斗图 |
| 树图 | `"treemap"` | `group_by` | 类别层级树图 |
| 旭日图 | `"sunburst"` | `hierarchy` | 产品结构旭日图 |

#### 可选参数

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

#### 智能布局算法

系统自动：
- 根据图表数量计算最优网格列数
- 智能分配图表位置
- 地图自动获得 2x1 大尺寸
- 饼图可自动纵向扩展
- 平衡布局避免空白

#### Dashboard 专业功能

| 功能 | 说明 |
|------|------|
| 🎨 **卡片式布局** | 现代化卡片设计，带阴影和悬停动画 |
| 🌓 **主题切换** | 深色/浅色主题，自动保存偏好 |
| 📱 **响应式设计** | 自动适配手机、平板、桌面 |
| 🔄 **自动刷新** | 可配置自动刷新间隔（默认 30 秒）|
| 📄 **导出 PDF** | 一键导出整个仪表盘为 PDF 文件 |
| 🔍 **图表搜索** | 按标题快速过滤图表 |
| ⬇️ **单独下载** | 每个图表支持下载为 PNG 图片 |
| 🍞 **Toast 通知** | 操作反馈、错误提示 |
| ⏳ **加载状态** | 智能加载骨架屏 |

#### Dashboard 布局示例

```
Grid Layout (columns: 3, row_height: 400px)
┌────────────────────────────────────────┐
│  [月度销售趋势 - 2x1]  │ [地区占比 - 1x2] │
│                        │                  │
├────────────────────────┤                  │
│  [产品类别对比 - 2x1]  │                  │
├────────────────────────┴──────────────────┤
│         [全国销售热力图 - 3x1]              │
└──────────────────────────────────────────┘
```

**位置配置说明**：

- `row`: 起始行（从 0 开始）
- `col`: 起始列（从 0 开始）
- `col_span`: 占用列数（默认 1）
- `row_span`: 占用行数（默认 1）

---

### 案例五：数据导出与报告生成

**场景**：导出查询结果或整表数据

```bash
# 导出整表
/export result.csv --table sales_2024

# 导出查询结果
/export summary.xlsx --query "SELECT region, SUM(amount) FROM sales GROUP BY region"

# 导出合并数据
/export merged.csv --tables sales_jan sales_feb sales_mar --output merged.csv
```

---

### 案例六：外部数据库连接

**场景**：连接 MySQL 生产数据库查询数据

**1. 创建连接配置**（`db_connections.txt`）：

```ini
[connections.mysql_prod]
type=mysql
host=localhost
port=3306
database=production
username=reader
password=${MYSQL_PASSWORD}
```

**2. 查询外部数据库**：

```bash
# 查看表列表
/db list-tables mysql_prod

# 查询数据
/db query mysql_prod "SELECT * FROM orders WHERE created_at > '2024-01-01'"

# 导入到 DuckDB
/db import mysql_prod "SELECT * FROM customers" --table customers_import
```

---

### 案例七：数据轮询刷新

**场景**：定时从 API 自动刷新数据

**1. 创建轮询配置**（`polling_config.txt`）：

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
```

**2. 管理轮询任务**：

```bash
# 启动轮询
/poll start polling_config.txt

# 查看状态
/poll status

# 手动刷新
/poll refresh

# 停止轮询
/poll stop
```

---

## 显性指令系统

本 Skill 支持双模式交互：**显性指令**和**模糊匹配**。

### 支持的指令

| 指令 | 别名 | 功能 | 示例 |
|------|------|------|------|
| `/import` | `/i`, `/导入` | 数据导入 | `/import data.xlsx` |
| `/query` | `/q`, `/sql`, `/查询` | SQL 查询 | `/query SELECT * FROM sales LIMIT 10` |
| `/chart` | `/c`, `/图表` | 图表生成 | `/chart bar 销售额按类别` |
| `/chart-list` | `/cl`, `/图表列表` | 查看支持的图表类型 | `/chart-list 3d` |
| `/dashboard` | `/db`, `/仪表盘` | 生成仪表盘 | `/dashboard config.txt` |
| `/export` | `/e`, `/导出` | 数据导出 | `/export result.csv --table sales` |
| `/tables` | `/t`, `/表` | 查看表结构 | `/tables sales` |
| `/history` | `/h`, `/历史` | 导入历史 | `/history --limit 20` |
| `/metrics` | `/m`, `/口径` | 指标管理 | `/metrics add 月活用户` |
| `/help` | `/?`, `/帮助` | 显示帮助 | `/help` |
| `/clean` | `/清理` | 清理旧数据 | `/clean --days 30` |
| `/poll` | `/轮询` | 轮询管理 | `/poll status` |
| `/start` | `/server`, `/启动服务` | 启动本地服务 | `/start` |
| `/stop` | `/停止服务` | 停止本地服务 | `/stop` |
| `/status` | `/状态` | 查看服务状态和链接 | `/status` |

### 模糊匹配关键词

| 意图 | 触发关键词 |
|------|-----------|
| 数据导入 | 上传、导入、import、load、打开文件 |
| SQL 查询 | 查询、筛选、统计、分组、排序、select |
| 图表生成 | 图表、可视化、画图、chart、plot、展示 |
| Dashboard | 仪表盘、dashboard、多图表、综合展示 |
| 数据导出 | 导出、下载、export、保存、输出 |

---

## 支持的图表类型完整列表

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

---

## 地图使用三层级架构

### 层级一：省份级别

**数据示例**：北京、上海、广东、浙江、江苏...

**使用方式**：

```json
{
    "series": [{
        "type": "map",
        "map": "china"
    }]
}
```

**地图文件**：`assets/echarts/china.js`

### 层级二：城市级别

**数据示例**：广州市、深圳市、东莞市、杭州市、宁波市...

**使用方式**：

```json
{
    "series": [{
        "type": "map",
        "map": "guangdong"
    }]
}
```

**地图文件**：`assets/echarts/guangdong.js`、`assets/echarts/zhejiang.js` 等

**可用省份**：34 个省份，每个包含所有城市数据（如广东包含 21 个城市）

### 层级三：区县街道级别

**数据示例**：天河区、南山区、街道名称...

**使用方式**：

```json
{
    "bmap": {
        "center": [113.33, 23.12],
        "zoom": 12,
        "roam": true
    },
    "series": [{
        "type": "scatter",
        "coordinateSystem": "bmap"
    }]
}
```

**依赖**：百度地图 AK（环境变量 `BAIDU_AK`）

**注意**：仅在此层级需要百度地图 AK，前两层使用本地静态资源即可

---

## SQL 函数参考

本 Skill 使用 **DuckDB** 作为 SQL 引擎，语法与 MySQL/PostgreSQL 有差异。

### 常见函数映射

| MySQL 函数 | DuckDB 替代 |
|-----------|-------------|
| `GROUP_CONCAT(col, sep)` | `string_agg(col, sep)` |
| `DATE_FORMAT(date, '%Y-%m')` | `strftime(date, '%Y-%m')` |
| `DATEDIFF(a, b)` | `date_diff('day', a, b)` |
| `NOW()` | `CURRENT_TIMESTAMP` 或 `today()` |
| `IFNULL(a, b)` | `COALESCE(a, b)` |
| `MOD(a, b)` | `a % b` |

**详细参考**：`references/SQL_FUNCTIONS_REFERENCE.md`

---

## 安装与配置

### 在线安装 vs 离线安装

| 方式 | 适用场景 | 命令 | 是否需要网络 |
|------|----------|------|:---:|
| 在线安装 | 网络良好 | `pip install -r requirements.txt` | ✅ 是 |
| 离线安装 | 网络差/无网络 | `bash scripts/install.sh --offline` | ❌ 否 |
| 核心依赖 | 仅需基础功能 | `bash scripts/install.sh --offline --core-only` | ❌ 否 |

> 💡 **离线包说明**：如果发布包 (`echart-skill_*.zip`) 内包含 `wheels/` 目录（约 323 MB），
> 用户端运行 `install.sh` / `install.bat` 时会自动检测并使用本地 wheels，完全跳过 PyPI 下载。
> 维护者生成离线包：`bash scripts/download_wheels.sh && bash package.sh --offline`。

### 通用安装步骤

1. 下载最新版本的 `echart-skill_*.zip` 压缩包并解压。
2. 根据你所使用的 Agent 平台，选择对应的安装方式。
3. 安装 Python 依赖：

   ```bash
   # macOS / Linux
   bash scripts/install.sh              # 在线（需网络）
   bash scripts/install.sh --offline    # 离线（需 wheels/ 目录）

   # Windows
   scripts\install.bat                  # 在线
   scripts\install.bat --offline        # 离线
   ```

### 各平台安装方法

#### Claude Code

**macOS / Linux:**
```bash
# 方法1：创建符号链接（推荐，方便更新）
ln -s /path/to/echart-skill ~/.claude/skills/echart-skill

# 方法2：直接复制
cp -r /path/to/echart-skill ~/.claude/skills/
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills"
Copy-Item -Recurse "C:\path\to\echart-skill" "$env:USERPROFILE\.claude\skills\"
```

在项目根目录创建 `CLAUDE.md`：

```markdown
# 项目说明

@~/.claude/skills/echart-skill/SKILL.md
```

#### Trae / WorkBuddy

**macOS / Linux:**
```bash
cp -r /path/to/echart-skill ~/.trae/skills/
# 或
cp -r /path/to/echart-skill ~/.workbuddy/skills/
```

**Windows (PowerShell):**
```powershell
Copy-Item -Recurse "C:\path\to\echart-skill" "$env:USERPROFILE\.trae\skills\"
Copy-Item -Recurse "C:\path\to\echart-skill" "$env:USERPROFILE\.workbuddy\skills\"
```

### 地图配置（可选）

如果需要生成精细维度的地图（区县、街道），请设置环境变量 `BAIDU_AK`：

```bash
# macOS/Linux
echo 'export BAIDU_AK=你的百度地图AK' >> ~/.zshrc
source ~/.zshrc
```

```cmd
:: Windows (CMD, 以管理员身份运行)
setx BAIDU_AK "你的百度地图AK"
```

免费申请地址：[百度地图开放平台](https://lbsyun.baidu.com/index.php?title=jspopularGL/guide/getkey)

### 应用配置（echart_config.txt）

首次运行时系统会自动创建 `echart_config.txt`（默认配置如下），可按需修改：

```ini
server.enabled=false
server.port_range=8100,8200
output.dir=outputs/html
baidu_ak=
```

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `server.enabled` | `false` | 是否在生成图表后启动本地 HTTP 预览服务 |
| `server.port_range` | `8100,8200` | 服务端口范围 |
| `output.dir` | `outputs/html` | 图表 HTML 输出目录（相对于项目根目录） |
| `baidu_ak` | `""` | 百度地图 AK（也可通过环境变量 `BAIDU_AK` 设置） |

> 💡 **提示**：
> - 服务关闭时，生成图表后直接显示文件绝对路径（`file:///...`）。
> - 所有图表 HTML 为**自包含单文件**，可在任意浏览器中离线打开。
> - `baidu_ak` 优先级：环境变量 `BAIDU_AK` > `echart_config.txt`。

---

## 常见问题 (FAQ)

**Q: 为什么导入大 Excel 时有点慢？**
A: 本技能为了应对"脏数据"，会在底层调用 `openpyxl` 来遍历并解开所有的合并单元格（Merged Cells）。这种物理层面的解析比直接读取纯数据稍慢，但能保证数据的完整性和准确性。

**Q: 我发现 Agent 修改错数据了，怎么恢复？**
A: 本技能内置了"后悔药"机制。你可以直接对 Agent 说："刚才那一步算错了，撤销"，Agent 会由于没有覆盖原表，直接回退到上一个表版本。

**Q: 支持连接外部的 MySQL 或 PostgreSQL 吗？**
A: 本技能目前默认使用本地 DuckDB 以追求开箱即用和零配置。DuckDB 采用列式存储，对分析型查询性能卓越。如果需要连接外部数据库，你可以让 Agent 修改生成的连接字符串，架构上是完全支持的。

**Q: 如何从 API 接口导入数据？**
A: 使用 `/import url` 命令，指定 URL 和格式即可导入。支持 Basic Auth 和 Bearer Token 认证。导入后可使用 `refresh` 命令刷新数据。

**Q: 如何创建多图表仪表盘？**
A: 创建一个 `.txt` 配置文件（内容可使用 JSON 结构表达复杂图表位置和配置），然后使用 `/dashboard` 命令生成即可。详见案例四示例。

**Q: 地图如何选择正确的层级？**
A: 省份数据用 `china.js`，城市数据用对应的省份 JS（如 `guangdong.js`），区县街道数据使用百度地图 API。系统会自动处理地图文件加载。

**Q: Dashboard 支持哪些交互功能？**
A: 支持主题切换（深色/浅色）、自动刷新、导出 PDF、图表搜索、单独下载图表等。所有功能都在 Dashboard 工具栏中提供。

---

## 功能清单

| 功能模块 | 脚本 | 说明 |
|---------|------|------|
| 数据导入 | `scripts/data_importer.py` | 支持 CSV/Excel/URL 导入，流式处理大文件 |
| 数据导出 | `scripts/data_exporter.py` | 导出为 CSV/Excel，支持 SQL 查询导出 |
| 图表生成 | `scripts/chart_generator.py` | 支持 ECharts 6.0 全量图表类型 |
| 仪表盘生成 | `scripts/dashboard_generator.py` | 多图表网格布局，专业 UI/UX 模板 |
| 甘特图生成 | `scripts/gantt_chart.py` | 简化 API，支持任务数组输入 |
| 数据合并 | `scripts/data_merger.py` | 合并多个表格，支持导出和入库 |
| 数据清洗 | `scripts/data_cleaner.py` | 清洗、去重、标准化 |
| 本地服务 | `scripts/server.py` | 本地 HTTP 服务，预览图表 |
| 服务管理 | `scripts/server_cli.py` | /start, /stop, /status 命令支持 |
| 业务口径 | `scripts/metrics_manager.py` | 持久化业务规则和指标定义 |
| 历史查看 | `scripts/history_viewer.py` | 查看导入历史、表结构、表关联关系 |
| 外部数据库 | `scripts/db_cli.py` | MySQL/PostgreSQL/MongoDB 连接与查询 |
| 数据轮询 | `scripts/polling_cli.py` | 定时刷新 HTTP API 或数据库数据 |
| 图表 CLI | `scripts/chart_cli.py` | 命令行图表导出工具 |
| Dashboard UI | `assets/dashboard/` | 专业 CSS/JS 模板 |

---

## 更新日志

详见 [RELEASE_NOTE.md](./RELEASE_NOTE.md)

---

## 许可证

MIT License
