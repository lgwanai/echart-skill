# 基础南丁格尔玫瑰图 / Nightingale Chart

**Category:** `pie`
**Example dir:** `pie-roseType-simple`
**Difficulty:** 2

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
option = {
  legend: {
    top: 'bottom'
  },
  toolbox: {
    show: true,
    feature: {
      mark: { show: true },
      dataView: { show: true, readOnly: false },
      restore: { show: true },
      saveAsImage: { show: true }
    }
  },
  series: [
    {
      name: 'Nightingale Chart',
      type: 'pie',
      radius: [50, 250],
      center: ['50%', '50%'],
      roseType: 'area',
      itemStyle: {
        borderRadius: 8
      },
      data: [
        { value: 40, name: 'rose 1' },
        { value: 38, name: 'rose 2' },
        { value: 32, name: 'rose 3' },
        { value: 30, name: 'rose 4' },
        { value: 28, name: 'rose 5' },
        { value: 26, name: 'rose 6' },
        { value: 22, name: 'rose 7' },
        { value: 18, name: 'rose 8' }
      ]
    }
  ]
};
```

## Relevant Debug Patterns
## #17
 — Pie 模板 roseType/RADIUS 类型错误导致空白
- **日期**：2026-06-13
- **现象**：09_Pie_Basic 空白，无任何图表
- **根因**：(1) `ROSE_TYPE: ""` → JS 中变成 `roseType: ''`（空字符串），ECharts 不接受空串，只接受 `false`/`'radius'`/`'area'`；(2) `RADIUS: "['40%','70%']"` 被 `_json_safe` 当作字符串处理，单引号 JSON 解析失败，输出为带转义的字符串而非数组
- **修复**：(1) `ROSE_TYPE: "false"` → `_json_safe` 识别为 JS keyword，输出 `false`；(2) `RADIUS` 改为 Python list `["40%","70%"]` → `_json_safe` 用 `json.dumps` 正确序列化为 JS 数组 `["40%","70%"]`；(3) **模板 `pie/basic.html` 增加防御**：`roseType` 默认为 `...

## #21
 — Sunburst 空白：RADIUS 字符串 + FOCUS 值非法
- **日期**：2026-06-13
- **现象**：20_Sunburst 一片空白
- **根因**：(1) `RADIUS: "['0%','90%']"` — 字符串假数组，同 #17 pie 的问题，`_json_safe` 将其当作字符串处理；(2) `FOCUS: "none"` — ECharts sunburst `emphasis.focus` 只接受 `'ancestor'` 或 `'descendant'`，不接受 `'none'`
- **修复**：(1) `RADIUS` 改为 `D(["0%","90%"])` — JSON 数组；(2) `FOCUS: "ancestor"`；(3) **模板增加防御**：`radius: {{RADIUS}} || ["0%","90%"]` 和 `focus: {{FOCUS}} || "ancestor"`

---
...

## Key Points
- This is an official ECharts example from `pie-roseType-simple/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
