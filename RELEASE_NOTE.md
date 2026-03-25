# Release Note - Echart Skill

## 🚀 新功能 (New Features)

* **图表地图彻底本地化（离线渲染）**
  * 新增中国全省份、直辖市及全球地图的离线 JS 资源 (`assets/echarts/*.js`)，彻底移除对外部 CDN 的强依赖。即使在无网络环境下，生成的中国地图、世界地图及各省份地图仍能完美呈现，彻底解决白屏问题。
  * `chart_generator.py` 现已支持自动侦测选项中的地域名称，并智能注入对应的本地地图资源文件。
* **精细维度地图的“AK 模式”回退机制**
  * 引入了强制的 **Map Fallback Rule**。当需要渲染城市级、街区级或小众国家的精细维度数据时（即本地静态 JS 无法覆盖的范围），自动回退并强制使用基于百度地图 API (bmap) 的渲染模式。
* **全面增强的数据导入能力**
  * 新增对 **WPS 数据文件 (`.et`)** 的原生支持。
  * 引入 `numbers-parser` 库，新增对 **Mac Numbers 文件 (`.numbers`)** 的原生支持。
  * 升级多工作表（Multi-Sheet）自动解析机制。现在导入 Excel/WPS/Numbers 文件时，将自动遍历所有 Sheet，并为每个 Sheet 在 SQLite 中创建独立的表，表名自动规整化处理。
* **全新的一键导出功能**
  * 新增 `scripts/data_exporter.py` 脚本，支持将 SQLite 数据库中的整表数据，或者执行特定 SQL 查询后的结果，一键导出为 `.csv` 或 `.xlsx` 格式。
* **业务口径管理能力**
  * 新增 `scripts/metrics_manager.py` 脚本与 `references/metrics.md` 知识库文件。支持随时追加和持久化保存用户的“统计口径”和“业务指标定义”，作为大模型生成精准 SQL 时的高质量上下文参考。

## 🛠️ 优化与修复 (Improvements & Fixes)

* **图表坐标系崩溃修复**：修复了在 ECharts 中尝试将饼图 (`pie`) 直接挂载到地理坐标系 (`geo`) 导致图表渲染崩溃白屏的问题，并在工作流中明确了必须使用 `scatter` 或 `effectScatter` 的规范。
* **百度 AK 类型错误规避**：针对百度地图服务报错状态码 `240` (APP 服务被禁用) 的问题，在规范中明确区分了“浏览器端 AK”与“服务端 AK”的使用场景，并提供了代码级的静态坐标 fallback 建议。
* **图表预览服务器资源泄漏修复**：重构了本地 HTTP Server 的启动检测机制。废弃了不可靠的本地临时状态文件，改为无状态的端口探测与专属健康检查接口 (`/__echart_skill_health`)。彻底解决了每次生成新图表时可能重复启动 Python 进程从而导致系统资源耗尽的严重 Bug，确保全局只复用一个轻量级 Server 实例。
* **图表生成引擎重构**：完全剥离了原有的冗余 ECharts Python 模板依赖（删除了 `echarts_templates` 目录），转为更加灵活和强大的纯 Prompt + 纯 JSON 参数生成模式，彻底解决了下钻图表返回时因对象绑定引发的报错（`TypeError: Cannot read properties of undefined`）。
* **隔离工作区输出**：更新了 `.gitignore` 和打包配置脚本 `package.sh`，强制隔离 `outputs/` 目录，防止测试数据或临时文件被错误地提交到 Git 仓库或打包到发布产物中。
* **文档完善**：全面更新了 `skill.md` 工作流指南与 `README.md`。新增了百度地图 API Key 的申请官方链接，并补充了未来功能迭代规划。

## 📅 迭代规划 (Roadmap)
* 计划增加对甘特图（Gantt Chart）等项目管理图表的支持。
* 计划支持通过 URL 直接读取和接入外部 API 接口数据。
* 计划支持将多个图表组合，一键生成完整的交互式数据大盘（Dashboard）。