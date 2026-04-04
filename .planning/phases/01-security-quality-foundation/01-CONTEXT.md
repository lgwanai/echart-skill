# Phase 1: Security & Quality Foundation - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

本阶段修复关键安全漏洞（SQL 注入、输入校验）并建立测试覆盖，确保用户可以信任系统处理敏感数据，所有核心工作流都有自动化测试验证。

**范围锚点：**
- 修复 SQL 注入漏洞 (data_exporter.py, data_cleaner.py)
- 添加输入校验（文件路径、表名、SQL 查询）
- 迁移 API Key 到环境变量
- 引入日志框架
- 搭建测试框架并达到 80% 覆盖率

**不在范围内：**
- 性能优化（Phase 2）
- 新功能开发（Phase 3-5）

</domain>

<decisions>
## Implementation Decisions

### 测试优先级
- **测试顺序：** 业务核心优先 — chart_generator.py + data_importer.py 最先测试
- **覆盖率目标：** 所有核心模块达到 80% 覆盖率
- **后续测试：** data_exporter.py, data_cleaner.py（安全相关）, server.py, metrics_manager.py

### 日志策略
- **日志框架：** structlog（结构化日志，便于 AI Agent 解析）
- **日志级别：** 标准级别 — INFO for 正常操作, WARNING for 节点问题, ERROR for 异常
- **输出位置：** 仅文件 — logs/echart-skill.log
- **结构化字段：** 基础字段（时间戳、级别、模块名）+ 操作上下文（文件路径、表名、SQL 摘要）+ 性能指标（执行耗时、数据量）+ 错误详情（堆栈、异常）

### 校验严格度
- **表名校验：** 严格白名单 — 仅允许字母、数字、下划线，且以字母开头
- **路径校验：** 严格路径限制 — 必须在项目目录内，拒绝 ../ 等路径穿越
- **错误语言：** 中文 — 符合现有代码风格

### 向后兼容性
- **API Key 迁移：** 环境变量优先 + 回退 — 优先读环境变量，回退到 config.txt
- **弃用策略：** 立即移除 config.txt 支持 — 明确告知用户需要迁移

</decisions>

<code_context>
## Existing Code Insights

### 需要修改的文件
- `scripts/data_exporter.py:26` — SQL 注入漏洞，f-string 直接拼接表名
- `scripts/data_cleaner.py:43` — SQL 注入漏洞，f-string 直接拼接表名
- `scripts/chart_generator.py:46` — 静默异常处理
- `scripts/server.py:41` — 静默异常处理
- `config.txt` — API Key 硬编码，需要迁移

### 可复用资产
- `scripts/metrics_manager.py` — 已有类型注解模式，可作为参考
- 现有的 `argparse` CLI 模式 — 保持一致

### 需要新建的模块
- `tests/` 目录 — pytest 测试框架
- `tests/conftest.py` — 测试 fixtures
- 日志配置模块 — 结构化日志

### 集成点
- 所有脚本需要引入日志框架
- 所有 SQL 操作需要经过校验层
- API Key 读取逻辑需要修改

</code_context>

<specifics>
## Specific Ideas

- 测试框架使用 pytest + pytest-cov，参考研究推荐的 pytest 9.0.2
- 日志框架使用 structlog 25.5.0，结构化输出便于 Agent 解析
- 输入校验使用 pydantic 2.12.5，与现有类型注解风格一致

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-security-quality-foundation*
*Context gathered: 2026-04-04*
