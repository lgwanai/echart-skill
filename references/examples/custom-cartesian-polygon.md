# 自定义多边形图 / Custom Cartesian Polygon

**Category:** `custom`
**Example dir:** `custom-cartesian-polygon`
**Difficulty:** 3

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
const data = [];
const dataCount = 7;
for (let i = 0; i < dataCount; i++) {
  data.push([
    echarts.number.round(Math.random() * 100),
    echarts.number.round(Math.random() * 400)
  ]);
}
option = {
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['bar', 'error']
  },
  dataZoom: [
    {
      type: 'slider',
      filterMode: 'none'
    },
    {
      type: 'inside',
      filterMode: 'none'
    }
  ],
  xAxis: {},
  yAxis: {},
  series: [
    {
      type: 'custom',
      renderItem: function (params, api) {
        if (params.context.rendered) {
          return;
        }
        params.context.rendered = true;
        let points = [];
        for (let i = 0; i < data.length; i++) {
          points.push(api.coord(data[i]));
        }
        let color = api.visual('color');
        return {
          type: 'polygon',
          transition: ['shape'],
          shape: {
            points: points
          },
          style: api.style({
            fill: color,
            stroke: echarts.color.lift(color, 0.1)
          })
        };
      },
      clip: true,
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
- This is an official ECharts example from `custom-cartesian-polygon/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
