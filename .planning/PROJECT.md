# Echart Skill 质量提升与功能扩展

## What This Is

Echart Skill 是一个专为 AI Agent 设计的本地数据分析与处理技能包，支持 CSV/Excel/WPS/Numbers 文件导入、DuckDB 本地数据引擎、ECharts 6.0 全量图表生成。本项目是一个开源项目，旨在帮助数据分析工作人员在保障数据隐私的前提下，高效完成数据处理和可视化任务。

## Core Value

**让数据分析工作人员能够安全、高效地完成从数据导入到可视化输出的全流程，数据绝不出域。**

## Current Milestone: v1.2 高级数据源

**Goal:** 让用户能够连接外部数据库、增强 HTTP 数据源能力、支持定时轮询自动刷新可视化

**Target features:**
- 外部数据库连接（MySQL、PostgreSQL、MongoDB、SQLite）
- HTTP JSON 增强（更多鉴权方式、HTTP 方法）
- 定时轮询自动刷新可视化

## Requirements

### Validated

v1.0 已交付并验证的功能：

**核心能力：**
- ✓ 本地 DuckDB 数据引擎 (从 SQLite 迁移)
- ✓ CSV/Excel/WPS/Numbers 文件导入（流式处理大文件）
- ✓ ECharts 6.0 全量图表模板支持
- ✓ 数据清洗、查询、导出基础能力
- ✓ 业务口径管理 (metrics)
- ✓ 中国省市及世界地图离线资源
- ✓ 数据合并能力（多表合并导出）
- ✓ 导入历史与元数据追踪（Markdown表格输出）

**安全与质量：**
- ✓ SQL 注入修复 (data_exporter.py, data_cleaner.py)
- ✓ 结构化日志 (structlog)
- ✓ 输入验证 (pydantic)
- ✓ API Key 环境变量化
- ✓ 测试覆盖率 80%+

**性能优化：**
- ✓ DuckDB 连接池与 WAL 模式
- ✓ 大文件流式导入
- ✓ 异步地理编码 API
- ✓ 服务进程生命周期管理

**可视化扩展：**
- ✓ Dashboard 多图表组合布局
- ✓ 甘特图 API
- ✓ URL/API 数据源导入

**v1.1 协作能力：**
- ✓ 仪表盘导出为独立HTML（全量数据嵌入）
- ✓ 单个图表导出为独立HTML（全量数据嵌入）
- ✓ 甘特图导出为独立HTML（全量数据嵌入）
- ✓ 导出命令 CLI 接口

### Active

v1.2 高级数据源需求：

**数据库连接：**
- [ ] MySQL 数据库连接
- [ ] PostgreSQL 数据库连接
- [ ] MongoDB 数据库连接
- [ ] SQLite 数据库连接（外部文件）

**HTTP 增强：**
- [ ] 更多鉴权方式（API Key、OAuth2）
- [ ] 更多 HTTP 方法（POST、PUT、DELETE）

**自动轮询：**
- [ ] 定时轮询数据源
- [ ] 自动刷新可视化

### Out of Scope

- 多用户认证系统 — 当前定位为单用户本地工具
- 云端数据存储 — 保持本地优先原则
- 移动端适配 — 专注桌面端体验
- PDF 导出 — 延后到 v1.3
- 实时协作编辑 — 保持本地优先
- 云数据库（RDS、云托管）— 仅支持直连自建数据库

## Context

**技术栈：** Python 3.x + DuckDB + ECharts 6.0，无需后端服务，纯本地执行。

**现有架构：**
- `scripts/data_importer.py` - 数据导入，支持多种格式
- `scripts/data_exporter.py` - 数据导出
- `scripts/chart_generator.py` - 图表生成核心
- `scripts/dashboard_generator.py` - 仪表盘生成
- `scripts/gantt_chart.py` - 甘特图生成
- `scripts/server.py` - 本地 HTTP 服务
- `scripts/data_cleaner.py` - 数据清理
- `scripts/data_merger.py` - 数据合并
- `scripts/history_viewer.py` - 历史查看
- `references/prompts/` - ECharts 图表模板

**v1.0 技术决策：**
- 使用 DuckDB 替代 SQLite（列式存储，分析性能更优）
- 使用 pytest + structlog（测试和日志）
- 使用 httpx 异步客户端（API 调用）
- 使用 pydantic 验证器（配置验证）

## Constraints

- **兼容性：** 必须保持对现有 Agent 平台的兼容 (OpenClaw, Claude Code, WorkBuddy, OpenCode, Trae)
- **本地优先：** 数据不出域原则不可打破
- **零配置：** 保持开箱即用体验
- **向后兼容：** API 变更需要平滑迁移

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 使用 pytest 作为测试框架 | Python 生态最成熟的测试框架，插件丰富 | ✓ Good |
| 日志框架选用 structlog | 结构化日志，AI agent 友好 | ✓ Good |
| Dashboard 采用网格布局 | 灵活且易于实现，符合 ECharts 生态 | ✓ Good |
| DuckDB 替代 SQLite | 列式存储，分析查询性能卓越 | ✓ Good |
| HTTP 导出使用全量数据嵌入 | 完全离线可用，无需服务器 | ✓ Good |
| 外部数据库连接架构 | 使用 SQLAlchemy + 连接池，支持多数据库 | — Pending |

---
*Last updated: 2026-04-12 after v1.2 milestone initialization*
