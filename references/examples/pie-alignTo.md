# 饼图标签对齐 / Pie Label Align

**Category:** `pie`
**Example dir:** `pie-alignTo`
**Difficulty:** 3

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
const data = [
  {
    name: 'Apples',
    value: 70
  },
  {
    name: 'Strawberries',
    value: 68
  },
  {
    name: 'Bananas',
    value: 48
  },
  {
    name: 'Oranges',
    value: 40
  },
  {
    name: 'Pears',
    value: 32
  },
  {
    name: 'Pineapples',
    value: 27
  },
  {
    name: 'Grapes',
    value: 18
  }
];
option = {
  title: [
    {
      text: 'Pie label alignTo',
      left: 'center'
    },
    {
      subtext: 'alignTo: "none" (default)',
      left: '16.67%',
      top: '75%',
      textAlign: 'center'
    },
    {
      subtext: 'alignTo: "labelLine"',
      left: '50%',
      top: '75%',
      textAlign: 'center'
    },
    {
      subtext: 'alignTo: "edge"',
      left: '83.33%',
      top: '75%',
      textAlign: 'center'
    }
  ],
  series: [
    {
      type: 'pie',
      radius: '25%',
      center: ['50%', '50%'],
      data: data,
      label: {
        position: 'outer',
        alignTo: 'none',
        bleedMargin: 5
      },
      left: 0,
      right: '66.6667%',
      top: 0,
      bottom: 0
    },
    {
      type: 'pie',
      radius: '25%',
      center: ['50%', '50%'],
      data: data,
      label: {
        position: 'outer',
        alignTo: 'labelLine',
        bleedMargin: 5
      },
      left: '33.3333%',
      right: '33.3333%',
      top: 0,
      bottom: 0
    },
    {
      type: 'pie',
      radius: '25%',
      center: ['50%', '50%'],
      data: data,
      label: {
        position: 'outer',
        alignTo: 'edge',
        margin: 20
      },
      left: '66.6667%',
      right: 0,
      top: 0,
      bottom: 0
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
- This is an official ECharts example from `pie-alignTo/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
