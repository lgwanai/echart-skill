# Echart Skill v2.1.0 — Enterprise Agent BI

**面向企业数据应用的本地优先 Agent BI 平替方案。**

它不是一个单纯的 ECharts 图表生成器，而是一套围绕企业数据分析全流程构建的本地 BI 能力包：数据导入、清洗、统计口径、数据质量、专家分析、洞察发现、预测归因、企业报告、交互式 Dashboard、审计和血缘追踪。

核心目标：让企业在不引入重型 BI 平台、不上传业务明细数据、不把数据交给大模型的前提下，用 AI Agent 完成专业、可复核、可交付的数据分析工作。

## 企业级定位

| 企业诉求 | echart-skill 的做法 |
|---|---|
| **替代传统 BI 的分析应用层** | 用 Agent + DuckDB + ECharts + 专家工作流生成仪表盘、报告、图表、洞察和导出文件 |
| **数据安全** | 数据分析在本地执行；业务明细数据默认不联网、不过大模型；大模型只负责规划、解释和生成代码/报告结构 |
| **可审计** | 查询访问、用户指令、脱敏状态、query hash、产物血缘均可记录，支持按日期生成审计报告 |
| **口径一致** | 支持全局/项目级统计口径；项目级口径只在记录的项目目录及子目录下生效 |
| **专业分析** | 内置销售、电商、增长、财务、运营、会员、营销、风控、数据质量等专家分析模式 |
| **强可视化** | 内置 ECharts 6 本地资源、27 类图表、354 个官方配方、地图/3D/关系图/桑基/漏斗/仪表盘等复杂图表 |
| **高质量输出** | Dashboard 与 Report 使用企业级 HTML 骨架、质量门校验、图表证据、附录数据和统计口径说明 |

## 安全与合规承诺

| 能力 | 说明 |
|---|---|
| **0 联网分析链路** | CSV/Excel/DuckDB 查询、清洗、统计、洞察、报告生成均在本地完成；自包含 HTML 离线可打开 |
| **0 明细过大模型** | 不把整表、明细行、原始文件内容塞进模型上下文；模型只接收 schema、聚合结果、样本级摘要或你显式提供的内容 |
| **PII 脱敏可控** | 脱敏默认关闭；可通过 `/privacy mask on` 开启手机号、邮箱、身份证、银行卡、薪资、地址等字段脱敏 |
| **审计报告** | `/audit-report --date YYYY-MM-DD` 输出当天用户指令、查询表、访问列、行数、脱敏状态、分类级别和 query hash |
| **数据血缘** | `/lineage` 记录报告、Dashboard、图表、导出文件对应的来源表、字段、统计口径和 query hash |
| **数据质量评分** | `/quality` 输出缺失率、重复行、常量列、疑似 ID 字段、质量分和分析限制 |

> 说明：如果用户显式配置外部数据库、HTTP/API 数据源或第三方地图地理编码，相关连接会按用户配置发起。默认本地分析与输出链路不依赖联网资源。

## 核心能力

| 模块 | 企业级能力 | 指令 |
|---|---|---|
| **Data Import & Cleaning** | Excel/CSV 导入、合并单元格处理、表名标准化、引导式清洗、非破坏式中间表 | `/import` `/clean` |
| **Semantic Scope** | 全局/项目级统计口径，保证不同报告和 Dashboard 使用同一指标定义 | `/scope` `/metrics` |
| **Data Quality** | 数据完整性、重复、常量列、疑似 ID、质量评分和限制说明 | `/quality` |
| **Insight Engine** | 自动发现趋势、异常、排名、构成、相关性、周期、变化，并输出置信度与限制 | `/analyze` `/insight` |
| **Expert Report** | 专家库驱动的金字塔结构企业报告，结论先行、图表举证、归因解释、行动建议 | `/report` |
| **Dashboard BI** | 自然语言生成企业级 Dashboard，支持 KPI、趋势、排行、结构、异常、地理、交互筛选 | `/dashboard` |
| **Forecast & Attribution** | 趋势预测、指标变化归因、贡献度分解、自动钻取建议 | `/forecast` `/why` |
| **Visualization Engine** | 27 类图表、354 个 ECharts 官方配方、本地地图、3D、关系图、桑基图、漏斗图等 | `/chart` `/chart-list` |
| **Audit & Lineage** | 指令审计、查询审计、产物血缘、query hash、审计报告 | `/audit-report` `/lineage` |
| **Context Manager** | 会话记忆和追问解析，支持“上个月呢”“和去年同期比”“深挖一下” | `/context` |

## 为什么适合作为企业 BI 平替

- **轻部署**：一个 Skill 包 + Python 依赖即可运行，不要求企业先部署完整 BI Server。
- **低数据风险**：分析计算落在本地 DuckDB，输出为本地文件；敏感数据不需要进入云端 BI 或大模型。
- **强分析深度**：不止展示指标，还能做质量检查、异常解释、变化归因、趋势预测和专家诊断。
- **强交付能力**：输出可直接交付的企业 HTML 报告、交互 Dashboard、图表 HTML、CSV/Excel 导出。
- **强治理能力**：统计口径、审计日志、数据血缘、质量报告让结果可追溯、可复核、可治理。
- **强可视化能力**：不是简单 matplotlib 图，而是企业级 ECharts 交互可视化，支持复杂业务场景。

---

## 📂 示例输出

`examples/` 目录包含基于「订单详情表」的 9 个完整案例：

| Case | 文件 | 说明 | 指令 |
|------|------|------|------|
| 1 | `case1_bar.html` | 各省份销售额柱状图 | `/chart bar` |
| 2 | `case2_pie.html` | 商品分类占比饼图 | `/chart pie` |
| 3 | `case3_line.html` | 渠道订单数折线图 | `/chart line` |
| 4 | `case4_map.html` | 全国销售分布地图 | `/chart map` |
| 5 | `case5_scatter.html` | 单价vs数量散点图 | `/chart scatter` |
| 6 | `case6_radar.html` | 渠道综合指标雷达图 | `/chart radar` |
| 7 | `case7_dashboard.html` | 订单数据分析仪表盘 | `/dashboard` |
| 8 | `case8_forecast.txt` | 销售额趋势预测 | `/forecast` |
| 9 | `case9_attribution.txt` | 销售额变化归因分析 | `/why` |

所有 HTML 文件均为自包含单文件，双击即可在浏览器打开。数据源：`examples/订单详情表.csv`（86 行 × 17 列）。

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

   > 💡 默认发布包不再内置 `wheels/`，依赖从 PyPI 在线安装；离线 wheels 如需使用，应作为单独归档提供。

   **在线安装（默认）：**
   ```bash
   # 完整安装（核心 + 可选依赖，约 100 MB）
   pip install -r requirements.txt

   # 或仅核心依赖（约 40 MB，覆盖 90% 场景）
   pip install -r requirements-core.txt
   ```

   **离线安装（需单独提供 wheels/ 目录）：**
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

### 🎯 .md 驱动生成（零模板，纯配方文件）

> ⛔ **每个 `.md` 是自包含图表配方——包含完整 JS 代码 + 数据替换点 + HTML 壳。Agent 只需 DuckDB 查数据 + 替换 data 数组。**

```
用户请求 "/chart bar 销售额"
 ↓
Step 1: DuckDB 查询真实数据 → 获取实际数据行
 ↓
Step 2: 查 references/examples/INDEX.md → 定位 {name}.md
 ↓
Step 3: 读 {name}.md → 提取 Complete Code（官方 JS，可直接运行）
 ↓
Step 4: 替换 data 数组为 DuckDB 真实数据
 ↓
Step 5: 包裹 HTML 壳（echarts inline + div#main + script）
 ↓
Step 6: 对照 docs/CHART_DEBUG_LOG.md 避坑
 ↓
Step 7: python scripts/validate_chart.py <output.html> 硬校验
 ↓
通过→返回用户 / 失败→修复→重试
```

### 🎯 三级生成策略

| 模式 | 触发条件 | 可靠度 | 说明 |
|------|---------|--------|------|
| 🟢 **配方模式** | 354 个 .md 配方覆盖了需求 | ★★★★★ | 直接替换 data JSON，零语法错误 |
| 🔵 **组合模式** | 多图表拼装到单页 | ★★★★★ | 多配方 + grid 布局组装 |
| 🟡 **知识库兜底** | 配方覆盖不到的需求 | ★★★★ | 知识片段 + 案例代码参考 |

### 🟢 配方模式（优先 — 27 种图表 × 354 个 .md 配方）

```
用户请求 → Agent 查 references/examples/INDEX.md → 定位 .md 配方 → DuckDB 查数据 → 替换 data → 生成 HTML
```

**Agent 只需替换 data 数组，不需要写任何 ECharts option 代码：**
- 每个 `.md` = 自包含图表配方（完整 JS + 数据替换点 + HTML 壳）
- data 格式由 .md 文件中的 `## Data Format` 章节定义
- 输出：单个自包含 HTML 文件，内联 ECharts 库（~1.1MB）

**内联机制：**

| 资源 | 注入方式 | 说明 |
|------|---------|------|
| echarts.min.js (1.1MB) | Agent 内联到 `<script>` | 全部图表 |
| 地图 JS (china.js 等) | Agent 内联到 `<script>` | 地图类型自动检测 |
| echarts-gl.min.js (625KB) | Agent 内联到 `<script>` | 3D 图表 |

**ECharts 稳定性铁律：**

- 只要 HTML 中出现 `echarts.init`，就必须在它之前内联完整的 `assets/echarts/echarts.min.js`。
- 禁止 `<script src="https://cdn.jsdelivr.net/.../echarts.min.js">`、`<script src="./echarts.min.js">`、运行时 `script.src = ...`。
- 禁止用占位 stub 冒充 ECharts 库；校验器必须看到真实内联库。
- `new echarts.graphic.LinearGradient(...)` / `RadialGradient(...)` 必须括号完整闭合，少一个 `)` 会导致整页图表脚本失败。
- `python scripts/validate_chart.py <output.html>` 失败时，不能返回用户，必须修复后重跑。

```bash
# Agent 自动生成自包含 HTML（inline ECharts + div#main + script）：
# Agent: DuckDB 查询 → .md 配方结构 → 替换 data → 包裹 HTML 壳 → 校验
# 输出：单个 .html 文件，双击浏览器即可打开，零外部依赖
```

### 🔵 组合模式

```
多个独立图表 → 各自走配方模式 → grid 布局组装 → 单 HTML 输出
```

### 🟡 知识库兜底（无 .md 配方时）

```
Step 1: 查 references/knowledge/INDEX.md → 定位知识文件
Step 2: 读知识片段（concepts/chart-types/api/patterns）→ 语法约束
Step 3: 读 354 案例 .md → 参考代码；冷门/归档资产从 DuckDB 资产库检索
Step 4: 知识 + 案例一起提交 → 生成完整 option
```

### 项目结构

```
echart-skill/
├── references/
│   ├── examples/            # 354 个 .md 自包含图表配方（唯一参考）
│   │   └── INDEX.md         # 配方映射决策表
│   ├── knowledge/           # 知识库
│   │   ├── INDEX.md         # 主索引
│   │   ├── concepts/  8 个  # 核心概念
│   │   ├── chart-types/  4 个 # 图表类型语法指南
│   │   ├── api/  6 个       # API 参考
│   │   ├── patterns/  10 个 # 最佳实践
│   │   └── examples/INDEX.md # 案例索引
├── workflow_specs/          # Agent 工作流规范
│   ├── dashboard_workflow.md   # Dashboard 规划流程
│   ├── report_workflow.md      # 报告生成流程
│   ├── data_cleaning_workflow.md # Agent 引导式数据清洗流程
│   ├── dashboard_runtime_quality.md # Dashboard 运行时质量门（硬性约束）
│   ├── dashboard_expert_library/ # Dashboard 专家库（5 个场景模板）
│   │   ├── INDEX.md              # Dashboard 专家动态匹配索引
│   │   ├── DASHBOARD_EXPERT_TEMPLATE.md # 用户自定义 Dashboard 专家模板
│   │   ├── sales_ecommerce_dashboard.md
│   │   ├── traffic_growth_dashboard.md
│   │   └── general_business_dashboard.md
│   ├── dashboard_modules/      # Dashboard 可复用分析模块
│   │   └── city_sales_map.md   # 城市销售/销量地图模块
│   ├── expert_library/         # Report 专家库（10 个领域专家）
│   │   ├── INDEX.md            # 专家动态匹配索引
│   │   ├── EXPERT_TEMPLATE.md   # 用户自定义专家模板
│   │   ├── sales_ecommerce.md   # 销售/电商
│   │   ├── traffic_growth.md    # 流量/增长
│   │   ├── finance_management.md # 财务管理
│   │   ├── marketing_campaign.md # 营销活动
│   │   ├── operations_fulfillment.md # 运营履约
│   │   ├── customer_membership.md   # 客户/会员
│   │   ├── product_content.md       # 产品内容
│   │   ├── risk_data_quality.md     # 风控/数据质量
│   │   └── general_management.md    # 通用经营
│   ├── html_templates/         # HTML 骨架模板
│   │   ├── report_light.html   # 默认企业 PDF 风格报告模板
│   │   └── dashboard_light.html # 默认企业 BI 仪表盘模板
│   └── visual_templates/       # 视觉方向（light/dark）
├── assets/                  # JS/CSS 资源和地图文件
├── scripts/                 # Python 工具脚本
├── tests/                   # 测试文件（40+ 测试文件）
└── outputs/                 # 输出目录（html/configs/reports）
```

### 案例检索

图表配方直接搜索 `references/examples/*.md` 文件，无需构建索引。

```bash
# 搜索图表配方
python scripts/reference_assets.py search "bar race" --limit 5

# 读取完整配方内容
python scripts/reference_assets.py get references/examples/bar-race.md

# 按图表类型列出
python scripts/reference_assets.py list --chart-type line --limit 20
```

---

## 核心功能与使用案例

### 案例一：数据导入与基础标准化

**场景**：上传销售数据 Excel，自动识别并导入。导入阶段只做表头、合并单元格、表名等基础标准化；业务清洗请使用 `/clean`。

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

### 案例二：Agent 引导式数据清洗

**场景**：导入后按业务规则清洗数据，例如统一日期和金额格式、按多列唯一键去重、校验字段逻辑和跨表一致性。

```bash
/clean orders --unique-key order_id,line_id --duplicate-keep latest --duplicate-order-by updated_at
/clean orders --config outputs/configs/orders_cleaning.json --output-table orders_cleaned
/clean orders --dry-run
```

Agent 会按 `workflow_specs/data_cleaning_workflow.md` 先询问必要规则，不会强行设定。例如：

- 唯一键是哪几列，重复时保留最新、首条、末条还是聚合？
- 日期字段是否统一为 DATE？
- 金额字段是否统一为两位小数，负数是否允许？
- 缺失值是删除、填补、保留还是标记？
- 是否需要规则校验，如 `start_date <= end_date`？
- 是否需要跨表验证，如注册日期早于首次购买日期？

支持的清洗能力包括：类型转换、缺失值处理、重复处理、异常值处理、归一化/标准化、文本一致性、规则引擎、跨表验证、派生特征和脱敏。

---

### 案例三：SQL 查询与数据分析

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

### 案例四：单图表生成

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

### 案例五：专业 Dashboard 生成（自然语言）

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

#### 方法二：Agent 驱动（推荐）

Agent 按 `workflow_specs/dashboard_workflow.md` 规划仪表盘，并必须读取 `workflow_specs/dashboard_runtime_quality.md` 作为运行时质量门；随后完整读取、使用 `workflow_specs/html_templates/dashboard_light.html` 作为企业 BI 页面骨架，再结合 `workflow_specs/visual_templates/light.md`（或 dark.md）控制视觉方向：

```
用户: /dashboard 创建销售分析仪表盘，包含地区柱状图和品类饼图
  → Agent 解析意图 → DuckDB 查询 → 建立 KPI 树 → 设计布局 → 生成自包含 HTML
```

生成的 HTML 必须能看出模板落地：统一背景、企业级 header、工具栏、KPI 网格、洞察卡、图表面板、诊断区域、语义色、打印/PDF 和响应式规则。不能输出浏览器默认样式或临时 demo 风格页面。

主题切换必须切换整页 `data-theme` 和 CSS token，不能只切换图表主题；页面背景、header、toolbar、KPI 卡片、图表面板、诊断区、按钮和 toast 都要跟随变化。如果元数据、字段名或样例值包含城市信息，并且存在销售额/交易额/GMV/金额/销量/数量类指标，Dashboard 必须读取 `workflow_specs/dashboard_modules/city_sales_map.md`，补充城市地图 + 销售/销量模块；地图坐标或本地地图覆盖不足时，需提示数据缺口并用城市排行柱图兜底。

Dashboard 标题必须来自用户请求、表名、文件名或真实字段，不能凭空生成数据里不存在的行业/品类标题。业务 Dashboard 在数据支持时至少包含 6 个分析模块，例如 KPI、趋势、排行/贡献、结构、交叉分析、异常/归因、地理模块（触发时）和数据口径说明；图表过少且没有字段不足说明时，需要重做。

#### 方法三：专家库动态匹配

Dashboard 不通过固定 Python 生成器生成。Agent 会读取 `workflow_specs/dashboard_expert_library/INDEX.md`，根据表名、字段、样例值和用户目标选择 Dashboard 专用专家，再完整读取对应专家 `.md` 文件，按专家模式建立 KPI 树、诊断模块、交互筛选和图表组合。

用户可复制 `workflow_specs/dashboard_expert_library/DASHBOARD_EXPERT_TEMPLATE.md` 创建自己的 Dashboard 专家文件，并在 `workflow_specs/dashboard_expert_library/INDEX.md` 登记触发词和适用场景。

例如：

```
/dashboard 创建电商数据仪表盘，包含：各渠道销售柱状图、产品类别饼图、日销售趋势折线图、全国订单分布地图
  → 读取专家库索引
  → 选择 sales_ecommerce + customer_membership/marketing_campaign 支撑专家
  → 计算 GMV、订单、客单价、转化、渠道、复购等指标
  → 生成含洞察卡片、异常提醒、对比归因和交互筛选的企业级 HTML
```

#### 常用图表模块

| 图表类型 | 关键词 | 必需参数 | 示例 |
|---------|--------|---------|------|
| 柱状图 | `"bar"` | `group_by` | 各地区销售柱状图 |
| 折线图 | `"line"` | `time_column` | 月度趋势折线图 |
| 饼图 | `"pie"` | `group_by` | 产品类别饼图 |
| 地图 | `"map"` | `geo_column` | 全国分布地图 |
| 城市销售/销量地图 | `"geo" / "effectScatter"` | 城市列 + 销售额/交易额/GMV/金额/销量/数量列 | 城市销售或销量分布 |
| 散点图 | `"scatter"` | `x_column`, `y_column` | 价格销量散点图 |
| 雷达图 | `"radar"` | `dimensions` | 产品评分雷达图 |
| 漏斗图 | `"funnel"` | `group_by` | 销售漏斗图 |
| 树图 | `"treemap"` | `group_by` | 类别层级树图 |
| 旭日图 | `"sunburst"` | `hierarchy` | 产品结构旭日图 |

图表选择由专家文件里的 `Dashboard Modules`、`Core Metrics`、`Required Data Checks` 决定。Python 只允许用于 DuckDB 查询、指标计算、异常检测、归因和 HTML 校验，不作为 Dashboard 最终渲染器。

#### Dashboard 运行时质量门

生成或修复 dashboard 时必须执行 `workflow_specs/dashboard_runtime_quality.md`：

- 禁止任何运行时外链：`<script src>`、`script.src = https...`、`fetch(https...)`、注入 CDN 脚本都不允许。
- 禁止非法全局声明：使用 `window.dashboardCharts = []`，不能写 `var window.dashboardCharts = []`。
- 地图必须使用本地内联地图文件，例如 `assets/echarts/china.js`；不得引用未定义的 `chinaGeoJSON`，不得远程 fetch GeoJSON。
- 城市地图必须保证城市字段值和坐标 key 对齐，例如数据是 `北京市`，坐标表也必须有 `北京市`。
- PDF 导出必须内联 `html2canvas` 和 `jsPDF`，并捕获导出异常，失败时提示并回退 `window.print()`。
- PDF 导出必须通过 `window.jspdf.jsPDF || window.jsPDF` 解析构造器，不允许裸 `new jsPDF(...)`；调用 `html2canvas` 时必须设置 `ignoreElements`，避免 toast/临时节点进入 PDF。
- Dashboard CSS 不使用 `color-mix()`、`oklch()`、`lab()` 等 html2canvas 可能无法解析的颜色函数，改用 hex/rgb/rgba token。
- 返回前必须跑 `python scripts/validate_chart.py <output.html>`；能使用浏览器自动化时，用 `file://` 打开验证无 SyntaxError、无 console error、图表 canvas 和地图 canvas 正常、PDF 下载和单图下载可执行。

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

### 案例六：企业级 Report 生成

**场景**：生成正式企业分析报告，而不是图表堆叠或表格汇总。

```bash
/report sales --format html --title "6月销售经营分析报告"
```

Report 由 Agent 按 `workflow_specs/report_workflow.md` 生成，必须遵守金字塔原理：

1. 先说结论：3-5 条可行动的业务结论
2. 再说发现：一般会有多个关键发现分支，按业务重要性排序
3. 每个发现分支内部也遵守金字塔：局部结论 -> 观察发现 -> 图表举证 -> 解释归因 -> 局部建议
4. 图表举证：每个关键发现优先用趋势图、柱图、瀑布图、漏斗图、热力图等直观表达
5. 交叉诊断：按专家库执行多维交叉，例如时间 x 渠道、品类 x 区域、客户 x 产品、活动 x 留存
6. 深度归因：说明异常、对比、贡献来源、下钻路径和不确定性
7. 行动建议：给出优先级、预期影响和需要补充的数据
8. 附录放数据：汇总所有分支用到的数据表、SQL、字段口径、样本数据、数据限制，并用 `A1/A2/A3` 编号

HTML 报告必须先读取并使用 `workflow_specs/html_templates/report_light.html` 作为页面骨架，再结合 `workflow_specs/visual_templates/light.md`（默认）或 `dark.md` 调整视觉方向，呈现为企业 PDF 风格：封面、一页纸结论、编号章节、图表证据、打印友好样式。每个图表必须读取 `references/examples/INDEX.md` 与对应图表配方 `.md` 后生成；表格不能替代主要举证图表；前文关键结论必须引用附录数据表，例如 `[Data A1]`。

每个分析模块必须展示口语化“统计口径说明”，说明数据范围、时间粒度、指标口径、分组维度、筛选条件和当前数据不能证明的内容，主文不展示 SQL。报告只能基于事实字段和用户给定定义下结论；没有目标、预算、漏斗、留存、ROI、SLA 等字段或定义时，不得创造目标达成率、预算偏差、漏斗转化、留存表现等概念。涉及季节性或外部因素时，证据不足时应表述为“补充节假日、活动投放、价格、库存、天气、渠道策略等数据后，可以进一步判断这是季节性波动还是外部因素导致”。

---

### 案例七：数据导出

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

### 案例八：外部数据库连接

**场景**：连接 PostgreSQL/MySQL/MongoDB 数据库，直接查询分析

**1. 使用 /dbconn 管理连接（推荐）：**

```bash
# 添加全局 PostgreSQL 连接
/dbconn add --name analytics --type postgresql --host localhost --database analytics --username reader --password '${PG_PASSWORD}'

# 添加项目级 MySQL 连接（仅当前目录生效）
/dbconn add --name prod --type mysql --host db.internal --database production --level project

# 列出当前生效的连接
/dbconn list

# 测试连接
/dbconn test analytics
```

**2. 直接查询外部数据库：**

```bash
# 查看远程库表结构
python scripts/db_cli.py list-tables analytics

# 直接查询（无需先导入 DuckDB）
python scripts/db_cli.py query analytics "SELECT channel, SUM(amount) FROM orders GROUP BY channel"

# 需要跨表 JOIN 或离线分析时才导入 DuckDB
python scripts/db_cli.py import analytics "SELECT * FROM customers" --table-name customers_import
```

**3. 三级配置体系：**

| 级别 | 配置文件路径 | 生效范围 |
|------|-------------|---------|
| **项目级** | `<当前项目>/.echart-skill/db_connections.txt` | 仅该项目目录及子目录 |
| **传统** | `<当前目录>/db_connections.txt` | 当前目录及父目录 |
| **全局** | `<echart-skill>/references/db_connections.txt` | 所有项目 |

项目级连接同名覆盖全局连接，密码使用 `${ENV_VAR}` 占位符。

**🆕 外部查询审计与隐私**：所有外部数据库查询自动经过 PrivacyGuard PII 检测/脱敏 + 审计日志记录（Query Hash、连接名、库类型、列、行数、脱敏状态）——与本地 DuckDB 查询使用同一审计 Pipeline。可通过 `/audit-report` 统一查看。

---

### 案例九：数据轮询刷新

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
| `/dbconn` | `/dbc`, `/连接` | 数据库连接管理（全局/项目级，支持 PostgreSQL/MySQL/MongoDB） | `/dbconn add --name pg --type postgresql` |
| `/schema` | `/sc`, `/表结构` | 表结构定义管理（全局/项目级，Agent SQL 上下文增强） | `/schema add --name orders --columns "id:INT:ID:pk"` |
| `/dashboard` | `/db`, `/仪表盘` | 生成仪表盘 | `/dashboard config.txt` |
| `/export` | `/e`, `/导出` | 数据导出 | `/export result.csv --table sales` |
| `/tables` | `/t`, `/表` | 查看表结构 | `/tables sales` |
| `/history` | `/h`, `/历史` | 导入历史 | `/history --limit 20` |
| `/metrics` | `/m`, `/口径` | 指标管理 | `/metrics add 月活用户` |
| `/scope` | `/统计口径`, `/口径设置` | 统计口径设置（全局/项目级） | `/scope set --level project --name GMV --desc "SUM(amount)"` |
| `/privacy` | `/隐私` | 隐私配置，脱敏默认关闭，可开启 | `/privacy mask on` |
| `/audit-report` | `/审计报告` | 按日期生成指令与查询审计报告 | `/audit-report --date 2026-06-27` |
| `/quality` | `/数据质量` | 数据质量评分与问题报告 | `/quality orders --format markdown` |
| `/lineage` | `/血缘` | 记录或查询产物数据血缘 | `/lineage list --table orders` |
| `/help` | `/?`, `/帮助` | 显示帮助 | `/help` |
| `/clean` | `/清洗`, `/清理` | 数据内容清洗或清理旧数据 | `/clean orders --config rules.json` |
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
| 离线安装 | 单独拿到了 wheels 归档 | `bash scripts/install.sh --offline` | ❌ 否 |
| 核心依赖 | 仅需基础功能 | `bash scripts/install.sh --core-only` | ✅ 是 |

> 💡 **离线包说明**：默认 skill 包不再内置 `wheels/`。如确实需要离线安装，维护者可单独运行 `bash scripts/download_wheels.sh` 生成 wheels 归档，并随包外分发。

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
privacy.enabled=true
privacy.mask_pii=false
privacy.audit_enabled=true
privacy.read_only=false
privacy.audit_log_path=logs/audit.log
baidu_ak=
```

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `server.enabled` | `false` | 是否在生成图表后启动本地 HTTP 预览服务 |
| `server.port_range` | `8100,8200` | 服务端口范围 |
| `output.dir` | `outputs/html` | 图表 HTML 输出目录（相对于项目根目录） |
| `privacy.enabled` | `true` | 是否启用隐私与审计管线 |
| `privacy.mask_pii` | `false` | 是否开启 PII 脱敏；默认关闭 |
| `privacy.audit_enabled` | `true` | 是否写入查询/指令审计日志 |
| `privacy.read_only` | `false` | 兼容旧配置的可选 SQL 变更保护开关；默认不启用权限或写入管理 |
| `privacy.audit_log_path` | `logs/audit.log` | 审计日志路径 |
| `baidu_ak` | `""` | 百度地图 AK（也可通过环境变量 `BAIDU_AK` 设置） |

> 💡 **提示**：
> - 服务关闭时，生成图表后直接显示文件绝对路径（`file:///...`）。
> - 所有图表 HTML 为**自包含单文件**，可在任意浏览器中离线打开。
> - `baidu_ak` 优先级：环境变量 `BAIDU_AK` > `echart_config.txt`。

### 统计口径与审计

统计口径分两级：

- 全局口径：`python scripts/metrics_manager.py set --level global --name "GMV" --desc "SUM(pay_amount)"`，写入 `references/metrics.md`，所有项目生效。
- 项目口径：`python scripts/metrics_manager.py set --level project --name "GMV" --desc "SUM(pay_amount)" --project-dir "$PWD"`，写入当前项目 `.echart-skill/metrics.md`，并登记项目目录。只有执行目录位于该项目目录或子目录时才生效。
- 查询当前生效口径：`python scripts/metrics_manager.py effective --cwd "$PWD"`。

脱敏默认关闭：设置 `privacy.mask_pii=true` 后，默认查询入口会按敏感列规则脱敏；`execute_query_raw()` 仅用于明确需要原始数据的内部计算。

审计报告：

```bash
python scripts/audit_report.py log-command "/report sales --format html" --cwd "$PWD" --status started
python scripts/audit_report.py report --date 2026-06-27 --days 1 --print
```

报告会输出当天记录到的用户指令、查询表、访问列、行数、脱敏状态、分类级别、变更操作标记和 query hash。

### 数据质量与血缘

数据质量评分：

```bash
python scripts/data_quality.py orders --db workspace.duckdb --format markdown --print
```

报告包含质量分、等级、缺失率、重复行、常量列、疑似 ID 字段和改进建议。生成企业报告或 Dashboard 前建议先跑质量评分；当等级为 C/D 或存在 high/critical 问题时，报告结论应标注为“初步判断”并说明数据限制。

数据血缘记录：

```bash
python scripts/lineage_manager.py record \
  --artifact outputs/reports/orders.html \
  --type report \
  --tables orders \
  --columns amount,region \
  --query "SELECT region, SUM(amount) FROM orders GROUP BY region" \
  --metrics GMV \
  --generated-by "/report orders"

python scripts/lineage_manager.py list --table orders
```

血缘记录写入 `outputs/lineage/lineage.jsonl`，记录产物路径、来源表、字段、query hash、统计口径和生成指令。默认不保存 SQL 明文，避免泄露敏感查询细节。

---

## 常见问题 (FAQ)

**Q: 为什么导入大 Excel 时有点慢？**
A: 本技能为了应对"脏数据"，会在底层调用 `openpyxl` 来遍历并解开所有的合并单元格（Merged Cells）。这种物理层面的解析比直接读取纯数据稍慢，但能保证数据的完整性和准确性。

**Q: 我发现 Agent 修改错数据了，怎么恢复？**
A: 本技能内置了"后悔药"机制。你可以直接对 Agent 说："刚才那一步算错了，撤销"，Agent 会由于没有覆盖原表，直接回退到上一个表版本。

**Q: 支持连接外部的 MySQL 或 PostgreSQL 吗？**
A: ✅ 完全支持。使用 `/dbconn` 指令管理 PostgreSQL/MySQL/MongoDB 连接（支持全局/项目级配置），直接查询外部数据库无需先导入 DuckDB。详见案例八。

**Q: 如何从 API 接口导入数据？**
A: 使用 `/import url` 命令，指定 URL 和格式即可导入。支持 Basic Auth 和 Bearer Token 认证。导入后可使用 `refresh` 命令刷新数据。

**Q: 如何创建多图表仪表盘？**
A: 创建一个 `.txt` 配置文件（内容可使用 JSON 结构表达复杂图表位置和配置），然后使用 `/dashboard` 命令生成即可。详见案例五示例。

**Q: 地图如何选择正确的层级？**
A: 省份数据用 `china.js`，城市数据用对应的省份 JS（如 `guangdong.js`），区县街道数据使用百度地图 API。系统会自动处理地图文件加载。

**Q: Dashboard 支持哪些交互功能？**
A: 支持主题切换（深色/浅色）、自动刷新、导出 PDF、图表搜索、单独下载图表等。所有功能都在 Dashboard 工具栏中提供。

---

## 功能清单

| 功能模块 | 脚本 / 来源 | 说明 |
|---------|------------|------|
| 数据导入 | `scripts/data_importer.py` | 支持 CSV/Excel/URL 导入，流式处理大文件 |
| 数据导出 | `scripts/data_exporter.py` | 导出为 CSV/Excel，支持 SQL 查询导出 |
| 图表生成 | Agent + `references/examples/*.md` | DuckDB → .md 配方 → 替换 data → 自包含 HTML |
| 仪表盘生成 | Agent + `workflow_specs/dashboard_workflow.md` + `dashboard_expert_library/` + `html_templates/` | 专家模式驱动的 KPI 树、诊断模块、多图表企业级 Dashboard |
| 报告生成 | Agent + `workflow_specs/report_workflow.md` + `expert_library/` + `html_templates/` + `visual_templates/` | 金字塔结构企业级报告，结论先行、图表举证、异常/对比/归因完整 |
| 洞察分析 | `scripts/insight_engine.py` | 自动发现 7 种洞察模式 |
| 趋势预测 | `scripts/forecast_engine.py` | 4 种预测方法，零外部 ML 依赖 |
| 归因分析 | `scripts/attribution_engine.py` | 指标变化贡献度分解 + 钻取建议 |
| 会话管理 | `scripts/context_manager.py` | 追问解析、时间引用、意图检测 |
| 语义建模 | `scripts/semantic_model.py` | 自然语言→SQL 映射，列自动分类 |
| 隐私保护 | `scripts/privacy_guard.py` | 列级 PII 识别与脱敏、查询审计日志、敏感级别记录 |
| 数据合并 | `scripts/data_merger.py` | 合并多个表格，支持导出和入库 |
| 数据清洗 | Agent + `workflow_specs/data_cleaning_workflow.md` + `scripts/data_cleaner.py` | 类型转换、缺失/重复/异常处理、多列唯一键排重、规则引擎、跨表验证、脱敏 |
| 本地服务 | `scripts/server.py` / `server_cli.py` | 本地 HTTP 服务，预览图表 |
| 业务口径 | `scripts/metrics_manager.py` | 持久化业务规则和指标定义，全局/项目级 |
| 数据库连接 | `scripts/db_manager.py` + `db_cli.py` | PostgreSQL/MySQL/MongoDB 连接管理，三级配置体系，直接查询 |
| 表结构定义 | `scripts/schema_manager.py` | 表结构定义管理（全局/项目级），Agent SQL 生成上下文增强 |
| 历史查看 | `scripts/history_viewer.py` | 查看导入历史、表结构、表关联关系 |
| 外部数据库 | `scripts/db_cli.py` | MySQL/PostgreSQL/MongoDB 连接与查询 |
| 数据轮询 | `scripts/polling_cli.py` | 定时刷新 HTTP API 或数据库数据 |
| 图表校验 | `scripts/validate_chart.py` | 硬校验：Single File / Dashboard / 渲染 |
| Dashboard 资源 | `assets/dashboard/` | CSS/JS 模板（html2canvas、jsPDF 等） |
| 工作流规范 | `workflow_specs/` | Dashboard/Report 工作流 + 专家库（10 领域 + 5 Dashboard 场景）+ 可复用模块 + HTML 模板 + 视觉方向 |

---

## 更新日志

详见 [RELEASE_NOTE.md](./RELEASE_NOTE.md)

---

## 许可证

MIT License
