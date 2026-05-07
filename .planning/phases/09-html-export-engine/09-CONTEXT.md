# Phase 9: HTML Export Engine - Context

**Gathered:** 2026-04-11
**Status:** Ready for planning

<domain>
## Phase Boundary

导出图表、仪表盘、甘特图为独立HTML文件，数据全量嵌入，完全离线可用。不涉及新的图表类型或编辑功能。

**明确范围：**
- 导出现有图表/仪表盘/甘特图
- 数据以JSON形式嵌入HTML
- 使用本地ECharts库（无CDN依赖）
- 导出命令CLI接口

**排除范围：**
- 新图表类型
- HTML内编辑功能
- 在线协作功能

</domain>

<decisions>
## Implementation Decisions

### HTML Output Style

**页面布局：**
- 全屏图表布局，无边距
- 图表占据整个视口
- 适合粘贴到报告或演示文稿

**标题与元信息：**
- 顶部包含图表标题
- 无其他元信息（导出时间、数据来源等）
- 保持简洁，专注图表本身

**ECharts主题：**
- 可配置主题（通过配置文件或参数指定）
- 默认使用ECharts默认主题
- 支持深色主题等常见选项

**交互功能：**
- 仅保留ECharts基础交互（缩放、tooltip、图例切换）
- 不添加数据表格切换
- 不添加图片导出按钮

### Claude's Discretion

- HTML模板的具体实现
- 标题样式（字体、大小、位置）
- 主题配置的传递方式
- 中文字体处理

</decisions>

<specifics>
## Specific Ideas

- "全屏图表适合粘贴到报告中" — 用户明确提到使用场景
- 保持简洁，专注图表本身，不要过多装饰

</specifics>

<deferred>
## Deferred Ideas

- PDF导出 — 属于 v1.2 范围
- 在线分享/协作编辑 — 违反本地优先原则
- 图表内数据编辑功能 — 超出当前范围

</deferred>

---

*Phase: 09-html-export-engine*
*Context gathered: 2026-04-11*
