# Release Note - Echart Skill

## v1.0.0 (2026-04-04)

### 🚀 新功能 (New Features)

#### 数据仪表盘 (Dashboard)
- **多图表组合布局**：新增 `scripts/dashboard_generator.py`，支持通过 JSON 配置文件一键生成包含多个图表的交互式仪表盘
- **CSS Grid 布局**：支持灵活的网格布局配置，可指定每个图表的行列位置和跨度
- **配置校验**：使用 pydantic 进行配置验证，自动检测图表位置重叠冲突
- **单 HTML 输出**：所有图表渲染在单个 HTML 文件中，支持任意浏览器打开

#### URL/API 数据源
- **HTTP 数据导入**：新增 URL 数据源导入能力，支持从 HTTP/HTTPS 端点导入 JSON/CSV 数据
- **认证支持**：支持 Basic Auth 和 Bearer Token 认证，使用 SecretStr 保护敏感凭证
- **JSON Schema 推断**：自动推断 JSON 响应的结构，支持嵌套对象展平（如 `user.name` → `user_name`）
- **数据刷新**：支持手动刷新 URL 数据源，自动追踪数据来源

#### 甘特图 (Gantt Chart)
- **简化 API**：新增 `scripts/gantt_chart.py`，提供简化的甘特图 API
- **任务数组输入**：只需提供任务名称、开始时间、结束时间即可生成甘特图
- **自动验证**：自动验证结束时间晚于开始时间
- **文档完善**：SKILL.md 新增甘特图使用场景和示例

#### 数据合并
- **多表合并**：新增 `scripts/data_merger.py`，支持将多个 SQLite 表格合并为一个
- **来源追踪**：自动添加 `_source_table` 列追踪每行数据来源
- **导出支持**：支持将合并后的数据导出为 CSV 或 Excel 文件
- **CLI 命令**：提供命令行接口，支持 `--tables`、`--target`、`--export` 等参数

### 🛡️ 安全增强 (Security)

- **SQL 注入修复**：修复了 `data_exporter.py` 和 `data_cleaner.py` 中的 SQL 注入漏洞，使用表名白名单验证
- **输入验证**：新增 `validators.py`，使用 pydantic 对文件路径、表名、SQL 查询进行严格验证
- **API Key 安全**：将百度地图 API Key 从配置文件迁移到环境变量，弃用硬编码方式
- **路径遍历防护**：修复了 `server.py` 文件服务中的路径遍历漏洞，拒绝 `../` 等路径穿越尝试

### ⚡ 性能优化 (Performance)

- **连接池**：新增 `DatabaseRepository` 类，使用连接池管理 SQLite 连接，支持自动清理
- **WAL 模式**：启用 SQLite WAL 模式，支持多 Agent 并发读取数据库
- **流式导入**：所有 Excel 文件使用流式导入，支持处理 100MB+ 大文件
- **分块处理**：Excel 导入使用 10,000 行/块的流式读取，平衡内存和性能
- **异步地理编码**：使用 httpx AsyncClient 实现异步地理编码 API 调用，支持 5 并发请求和指数退避重试
- **服务进程管理**：新增 PID 文件追踪和 5 分钟无活动自动关闭机制

### 📝 质量提升 (Quality)

- **测试覆盖**：新增 pytest 测试框架，核心模块测试覆盖率达到 80%+
- **结构化日志**：使用 structlog 替代所有 print() 语句，日志输出为 JSON 格式便于 AI Agent 解析
- **异常处理**：消除静默异常处理，所有异常都记录到日志文件
- **文档完善**：全面更新 SKILL.md、README.md，新增功能使用指南

### 📊 功能模块清单

| 功能 | 脚本 | 状态 |
|-----|------|------|
| 数据导入 | `data_importer.py` | ✅ 增强（流式导入、URL导入） |
| 数据导出 | `data_exporter.py` | ✅ 安全修复 |
| 图表生成 | `chart_generator.py` | ✅ 稳定 |
| 仪表盘生成 | `dashboard_generator.py` | ✅ 新增 |
| 甘特图生成 | `gantt_chart.py` | ✅ 新增 |
| 数据合并 | `data_merger.py` | ✅ 新增 |
| 数据清洗 | `data_cleaner.py` | ✅ 安全修复 |
| 本地服务 | `server.py` | ✅ 安全修复、进程管理 |
| 数据库管理 | `database.py` | ✅ 新增（连接池） |
| 验证器 | `validators.py` | ✅ 新增 |
| 日志配置 | `logging_config.py` | ✅ 新增 |
| 业务口径 | `metrics_manager.py` | ✅ 稳定 |
| 异步地理编码 | `async_geocoding.py` | ✅ 新增 |

### 🔧 技术债务清理

- 移除 `echarts_templates` 目录，转为纯 Prompt + JSON 参数生成模式
- 隔离 `outputs/` 目录，防止测试数据混入 Git
- 统一 CLI 命令风格，保持一致的参数命名

---

## 历史版本

### v0.9.0

* **图表地图彻底本地化（离线渲染）**
  * 新增中国全省份、直辖市及全球地图的离线 JS 资源 (`assets/echarts/*.js`)，彻底移除对外部 CDN 的强依赖。即使在无网络环境下，生成的中国地图、世界地图及各省份地图仍能完美呈现，彻底解决白屏问题。
  * `chart_generator.py` 现已支持自动侦测选项中的地域名称，并智能注入对应的本地地图资源文件。
* **精细维度地图的"AK 模式"回退机制**
  * 引入了强制的 **Map Fallback Rule**。当需要渲染城市级、街区级或小众国家的精细维度数据时（即本地静态 JS 无法覆盖的范围），自动回退并强制使用基于百度地图 API (bmap) 的渲染模式。
* **全面增强的数据导入能力**
  * 新增对 **WPS 数据文件 (`.et`)** 的原生支持。
  * 引入 `numbers-parser` 库，新增对 **Mac Numbers 文件 (`.numbers`)** 的原生支持。
  * 升级多工作表（Multi-Sheet）自动解析机制。现在导入 Excel/WPS/Numbers 文件时，将自动遍历所有 Sheet，并为每个 Sheet 在 SQLite 中创建独立的表，表名自动规整化处理。
* **全新的一键导出功能**
  * 新增 `scripts/data_exporter.py` 脚本，支持将 SQLite 数据库中的整表数据，或者执行特定 SQL 查询后的结果，一键导出为 `.csv` 或 `.xlsx` 格式。
* **业务口径管理能力**
  * 新增 `scripts/metrics_manager.py` 脚本与 `references/metrics.md` 知识库文件。支持随时追加和持久化保存用户的"统计口径"和"业务指标定义"，作为大模型生成精准 SQL 时的高质量上下文参考。

### 🛠️ 优化与修复 (Improvements & Fixes)

* **图表坐标系崩溃修复**：修复了在 ECharts 中尝试将饼图 (`pie`) 直接挂载到地理坐标系 (`geo`) 导致图表渲染崩溃白屏的问题，并在工作流中明确了必须使用 `scatter` 或 `effectScatter` 的规范。
* **百度 AK 类型错误规避**：针对百度地图服务报错状态码 `240` (APP 服务被禁用) 的问题，在规范中明确区分了"浏览器端 AK"与"服务端 AK"的使用场景，并提供了代码级的静态坐标 fallback 建议。
* **图表预览服务器资源泄漏修复**：重构了本地 HTTP Server 的启动检测机制。废弃了不可靠的本地临时状态文件，改为无状态的端口探测与专属健康检查接口 (`/__echart_skill_health`)。彻底解决了每次生成新图表时可能重复启动 Python 进程从而导致系统资源耗尽的严重 Bug，确保全局只复用一个轻量级 Server 实例。
* **图表生成引擎重构**：完全剥离了原有的冗余 ECharts Python 模板依赖（删除了 `echarts_templates` 目录），转为更加灵活和强大的纯 Prompt + 纯 JSON 参数生成模式，彻底解决了下钻图表返回时因对象绑定引发的报错（`TypeError: Cannot read properties of undefined`）。
* **隔离工作区输出**：更新了 `.gitignore` 和打包配置脚本 `package.sh`，强制隔离 `outputs/` 目录，防止测试数据或临时文件被错误地提交到 Git 仓库或打包到发布产物中。
* **文档完善**：全面更新了 `skill.md` 工作流指南与 `README.md`。新增了百度地图 API Key 的申请官方链接，并补充了未来功能迭代规划。
