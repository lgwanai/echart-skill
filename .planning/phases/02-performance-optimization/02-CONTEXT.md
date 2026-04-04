# Phase 2: Performance Optimization - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

本阶段优化系统性能，确保用户可以导入和处理大数据集（100MB+ Excel 文件）而不会遇到内存问题或阻塞操作。

**范围锚点：**
- 大文件流式导入（Excel 文件）
- SQLite 连接池
- 异步地理编码 API 调用
- 服务进程管理
- SQLite WAL 模式

**不在范围内：**
- 新功能开发（Phase 3-5）
- UI/UX 改进

</domain>

<decisions>
## Implementation Decisions

### 大文件处理策略
- **流式导入：** 始终使用流式导入 — 避免 Excel 文件内存问题
- **分块大小：** 10,000 行/块 — 每块约 1-2MB，平衡内存和性能
- **CSV 处理：** 已有分块导入（chunksize=50000），保持现有逻辑

### 连接池配置
- **连接池大小：** 5 个连接 — 单进程场景足够
- **WAL 模式：** 启用 — 允许读写并发，多 Agent 同时访问数据库
- **连接超时：** 使用默认 5 秒

### 异步 API 配置
- **并发数：** 5 并发 — 百度 API 默认 QPS 限制
- **重试策略：** 3 次重试，指数退避（1s, 2s, 4s）
- **超时时间：** 10 秒单次请求超时
- **使用 httpx 异步客户端**

### 服务进程管理
- **PID 文件位置：** outputs/pids/ — 与其他输出文件一致
- **进程超时：** 5 分钟无请求后自动关闭
- **端口清理：** 启动时检查并清理僵尸进程

</decisions>

<code_context>
## Existing Code Insights

### 需要修改的文件
- `scripts/data_importer.py` — 添加 Excel 流式导入
- `scripts/chart_generator.py` — 异步地理编码 API 调用
- `scripts/server.py` — PID 文件管理和进程超时
- 新建 `database.py` — 连接池管理

### Phase 1 建立的基础
- `validators.py` — 输入校验（可复用）
- `logging_config.py` — 日志框架（包含性能指标字段）
- `tests/` — 测试框架（可测试性能代码）

### 技术栈（来自研究）
- httpx 0.28.1 — 异步 HTTP 客户端
- tenacity — 重试逻辑

</code_context>

<specifics>
## Specific Ideas

- 使用 openpyxl 的 read_only 模式实现 Excel 流式读取
- 使用 asyncio.gather() 并发执行地理编码请求
- 使用上下文管理器管理数据库连接池

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-performance-optimization*
*Context gathered: 2026-04-04*
