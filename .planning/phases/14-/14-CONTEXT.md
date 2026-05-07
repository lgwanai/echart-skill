# Phase 14: 服务启动和关闭指令支持 - Context

**Gathered:** 2026-05-07
**Status:** Ready for planning
**Source:** User request

<domain>
## Phase Boundary

本 Phase 旨在解决生成的图表页面需要本地服务才能访问的问题，通过添加服务启动和关闭指令，让用户可以方便地管理本地服务，重启电脑后可以重新启动服务查看已生成的页面。

### 核心需求
1. 添加 `/start` 或 `/server` 指令启动本地 HTTP 服务
2. 添加 `/stop` 指令关闭本地服务
3. 服务启动后显示所有可访问的图表链接列表
4. 服务状态持久化（重启后可重新启动）
5. 与现有的 `scripts/server.py` 集成

### 背景问题
- 目前生成的 HTML 图表需要通过 `scripts/server.py` 启动本地服务才能查看
- 用户重启电脑后，服务停止，之前生成的页面无法访问
- 用户不知道当前有哪些图表可以访问
- 缺少统一的服务管理指令

</domain>

<decisions>
## Implementation Decisions

### 1. 指令设计
- **`/start`** (别名 `/server`, `/启动服务`) - 启动本地 HTTP 服务
- **`/stop`** (别名 `/停止服务`) - 停止本地服务
- **`/status`** (别名 `/状态`) - 查看服务状态和可访问的链接列表

### 2. 服务管理
- 使用 `scripts/server.py` 作为底层服务
- 服务状态持久化到 `outputs/.server_status.json`
- 记录服务 PID、端口、启动时间、图表列表

### 3. 链接列表显示
- 扫描 `outputs/html/` 目录获取所有图表文件
- 生成可访问的 URL 列表 (http://localhost:PORT/filename.html)
- 支持按文件名、创建时间排序

### 4. 与 SKILL.md 集成
- 在 SKILL.md 的显性指令系统中添加新指令
- 更新 README.md 说明服务管理功能

### Claude's Discretion
- 端口冲突处理策略
- 服务异常退出的自动重启
- 多服务实例管理

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### 现有实现
- `scripts/server.py` - 现有的本地 HTTP 服务器实现
- `SKILL.md` - 显性指令系统设计
- `README.md` - 项目说明文档

### 技术参考
- Python `http.server` 模块
- 进程管理（PID 文件）
- 服务状态持久化

</canonical_refs>

<specifics>
## Specific Ideas

### 启动服务流程
```
用户输入: /start
    │
    ├─ 检查是否已有服务运行
    │   ├─ 是 → 显示服务状态和链接列表
    │   └─ 否 → 启动新服务
    │
    ├─ 启动 scripts/server.py (后台运行)
    │
    ├─ 保存服务状态到 outputs/.server_status.json
    │   ├─ PID
    │   ├─ 端口 (默认 8000)
    │   ├─ 启动时间
    │   └─ 图表列表
    │
    └─ 扫描 outputs/html/ 目录
        └─ 显示所有可访问的图表链接
```

### 停止服务流程
```
用户输入: /stop
    │
    ├─ 读取 outputs/.server_status.json
    │
    ├─ 检查服务是否运行
    │   ├─ 否 → 显示 "服务未运行"
    │   └─ 是 → 发送终止信号
    │
    ├─ 清理 PID 文件
    │
    └─ 显示 "服务已停止"
```

### 状态查询流程
```
用户输入: /status
    │
    ├─ 检查服务状态
    │   ├─ 运行中 → 显示端口、运行时间
    │   └─ 未运行 → 提示使用 /start 启动
    │
    └─ 显示可访问的图表列表
        ├─ 文件名
        ├─ 访问 URL
        ├─ 创建时间
        └─ 文件大小
```

</specifics>

<deferred>
## Deferred Ideas

- 远程访问支持（ngrok 集成）
- 服务配置持久化（端口、目录）
- 图表分类和搜索功能
- 服务监控和自动重启

</deferred>

---

*Phase: 14-服务启动和关闭指令支持*
*Context gathered: 2026-05-07*
