# Echart Skill 质量提升与功能扩展

## What This Is

Echart Skill 是一个专为 AI Agent 设计的本地数据分析与处理技能包，支持 CSV/Excel/WPS/Numbers 文件导入、SQLite 本地数据引擎、ECharts 6.0 全量图表生成。本项目是一个开源项目，旨在帮助数据分析工作人员在保障数据隐私的前提下，高效完成数据处理和可视化任务。

## Core Value

**让数据分析工作人员能够安全、高效地完成从数据导入到可视化输出的全流程，数据绝不出域。**

## Requirements

### Validated

- ✓ 本地 SQLite 数据引擎 - 现有
- ✓ CSV/Excel/WPS/Numbers 文件导入 - 现有
- ✓ ECharts 6.0 全量图表模板支持 - 现有
- ✓ 数据清洗、查询、导出基础能力 - 现有
- ✓ 业务口径管理 (metrics) - 现有
- ✓ 中国省市及世界地图离线资源 - 现有

### Active

**代码质量与安全性：**
- [ ] 修复 SQL 注入风险 (data_exporter.py, data_cleaner.py)
- [ ] 完善异常处理，消除静默异常
- [ ] 引入日志框架替代 print 语句
- [ ] 输入验证 (文件路径、表名、SQL 查询)

**性能优化：**
- [ ] 大文件流式导入，避免内存溢出
- [ ] 异步地理编码 API 调用
- [ ] SQLite 连接池/上下文管理器
- [ ] 服务进程清理机制，避免端口耗尽

**功能扩展：**
- [ ] Dashboard 多图表组合布局
- [ ] 甘特图支持
- [ ] URL/API 数据源接入
- [ ] 团队协作分享能力

**测试覆盖：**
- [ ] 单元测试框架搭建 (pytest)
- [ ] 核心模块测试覆盖 (chart_generator, data_importer, server)
- [ ] 集成测试覆盖 (端到端流程)
- [ ] 测试覆盖率达到 80%+

### Out of Scope

- 多用户认证系统 — 当前定位为单用户本地工具
- 云端数据存储 — 保持本地优先原则
- 外部数据库连接 (MySQL/PostgreSQL) — 保持开箱即用
- 移动端适配 — 专注桌面端体验

## Context

**技术栈：** Python 3.x + SQLite + ECharts 6.0，无需后端服务，纯本地执行。

**现有架构：**
- `scripts/data_importer.py` - 数据导入，支持多种格式
- `scripts/data_exporter.py` - 数据导出
- `scripts/chart_generator.py` - 图表生成核心
- `scripts/server.py` - 本地 HTTP 服务
- `scripts/data_cleaner.py` - 数据清理
- `references/prompts/` - ECharts 图表模板

**已知问题 (from codebase mapping)：**
- SQL 注入风险在 data_exporter.py:26 和 data_cleaner.py:43
- 多处静默异常处理 (chart_generator.py:46, server.py:41)
- 百度 API Key 硬编码在 config.txt
- 无测试框架和测试用例
- 同步 API 调用影响性能
- 服务端口范围有限 (8100-8200)

## Constraints

- **兼容性：** 必须保持对现有 Agent 平台的兼容 (OpenClaw, Claude Code, WorkBuddy, OpenCode, Trae)
- **本地优先：** 数据不出域原则不可打破
- **零配置：** 保持开箱即用体验
- **向后兼容：** API 变更需要平滑迁移

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 使用 pytest 作为测试框架 | Python 生态最成熟的测试框架，插件丰富 | — Pending |
| 日志框架选用 logging 模块 | Python 标准库，无额外依赖 | — Pending |
| Dashboard 采用网格布局 | 灵活且易于实现，符合 ECharts 生态 | — Pending |

---
*Last updated: 2026-04-04 after initialization*
