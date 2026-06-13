# 利润分布直方图 / Profit

**Category:** `custom`
**Example dir:** `custom-profit`
**Difficulty:** 1

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
const colorList = [
  '#4f81bd',
  '#c0504d',
  '#9bbb59',
  '#604a7b',
  '#948a54',
  '#e46c0b'
];
const data = [
  [10, 16, 3, 'A'],
  [16, 18, 15, 'B'],
  [18, 26, 12, 'C'],
  [26, 32, 22, 'D'],
  [32, 56, 7, 'E'],
  [56, 62, 17, 'F']
].map(function (item, index) {
  return {
    value: item,
    itemStyle: {
      color: colorList[index]
    }
  };
});
option = {
  title: {
    text: 'Profit',
    left: 'center'
  },
  tooltip: {},
  xAxis: {
    scale: true
  },
  yAxis: {},
  series: [
    {
      type: 'custom',
      renderItem: function (params, api) {
        var yValue = api.value(2);
        var start = api.coord([api.value(0), yValue]);
        var size = api.size([api.value(1) - api.value(0), yValue]);
        var style = api.style();
        return {
          type: 'rect',
          shape: {
            x: start[0],
            y: start[1],
            width: size[0],
            height: size[1]
          },
          style: style
        };
      },
      label: {
        show: true,
        position: 'top'
      },
      dimensions: ['from', 'to', 'profit'],
      encode: {
        x: [0, 1],
        y: 2,
        tooltip: [0, 1, 2],
        itemName: 3
      },
      data: data
    }
  ]
};
```

## Relevant Debug Patterns
## #32
 — Error Bar 空白：custom renderItem 函数无法通过占位符传递
- **日期**：2026-06-13
- **现象**：39_Custom_Error_Bar 空白
- **根因**：(1) `RENDER_ITEM: "false"` → 无渲染函数，custom 类型不知道该画什么；(2) 多行 JS 函数无法通过 Python 字符串占位符传递（换行导致语法错误）
- **修复**：(1) `renderItem` 直接硬编码在模板中；(2) 模板简化为只需 `DATA` 占位符；(3) 误差线红色 `#e54035`，柱体蓝色 `#5470c6`

---
...

## Key Points
- This is an official ECharts example from `custom-profit/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
