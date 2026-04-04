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

## 安装方式

将本 Skill 包导入到你的 Agent 平台的技能（Skills）库中即可：

1. 下载最新版本的 `echart-skill_*.zip` 压缩包并解压。
2. 根据你所使用的 Agent 平台：
   - **Trae**: 将解压后的文件夹放入 `~/.trae/skills/` 目录下。
   - **Claude Code / OpenClaw / WorkBuddy**: 查阅对应平台关于"如何安装自定义 Skill/Tool"的官方文档，将本目录挂载或配置入其上下文中。
3. **地图配置（可选）**：如果需要生成中国地图相关的图表，请设置环境变量 `BAIDU_AK`。你可以前往 [百度地图开放平台](https://lbsyun.baidu.com/index.php?title=jspopularGL/guide/getkey) 免费申请 AK。
   ```bash
   # 设置环境变量（推荐）
   export BAIDU_AK=你的百度地图AK
   
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
A: 创建一个 JSON 配置文件，定义图表位置和配置，然后使用 `dashboard_generator.py` 生成即可。详见 `references/prompts/dashboard.md`。

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
