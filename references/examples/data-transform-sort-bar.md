# 柱状图排序 / Sort Data in Bar Chart

**Category:** `dataset, bar, transform`
**Example dir:** `data-transform-sort-bar`
**Difficulty:** 0

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
option = {
  dataset: [
    {
      dimensions: ['name', 'age', 'profession', 'score', 'date'],
      source: [
        ['Hannah Krause', 41, 'Engineer', 314, '2011-02-12'],
        ['Zhao Qian', 20, 'Teacher', 351, '2011-03-01'],
        ['Jasmin Krause ', 52, 'Musician', 287, '2011-02-14'],
        ['Li Lei', 37, 'Teacher', 219, '2011-02-18'],
        ['Karle Neumann', 25, 'Engineer', 253, '2011-04-02'],
        ['Adrian Groß', 19, 'Teacher', '-', '2011-01-16'],
        ['Mia Neumann', 71, 'Engineer', 165, '2011-03-19'],
        ['Böhm Fuchs', 36, 'Musician', 318, '2011-02-24'],
        ['Han Meimei', 67, 'Engineer', 366, '2011-03-12']
      ]
    },
    {
      transform: {
        type: 'sort',
        config: { dimension: 'score', order: 'desc' }
      }
    }
  ],
  xAxis: {
    type: 'category',
    axisLabel: { interval: 0, rotate: 30 }
  },
  yAxis: {},
  series: {
    type: 'bar',
    encode: { x: 'name', y: 'score' },
    datasetIndex: 1
  }
};
```

## Relevant Debug Patterns
## #23
 — Boxplot 空白：依赖缺失的 ecStat 库
- **日期**：2026-06-13
- **现象**：24_Boxplot 一片空白
- **根因**：原模板使用 ECharts `transform: { type: 'boxplot' }`，需要 `ecStat` 扩展库，但项目中不存在该库
- **修复**：(1) 模板重写为预计算五数概括格式 `series.data: [[min, Q1, median, Q3, max], ...]`，无需 ecStat；(2) 数据从原始值改为 `[[740,880,935,980,1070],[800,860,900,940,960]]`

---
...

## Key Points
- This is an official ECharts example from `data-transform-sort-bar/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
