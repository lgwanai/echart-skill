# bar-polar-label-tangential

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-polar-label-tangential

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

**2 data arrays** to replace:
- `data[0]`: `data: ['a', 'b', 'c', 'd']`
- `data[1]`: `data: [2, 1.2, 2.4, 3.6]`

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Tangential Polar Bar Label Position
titleCN: 极坐标柱状图标签
category: bar
difficulty: 2
*/
option = {
  title: [
    {
      text: 'Tangential Polar Bar Label Position (middle)'
    }
  ],
  polar: {
    radius: [30, '80%']
  },
  angleAxis: {
    max: 4,
    startAngle: 75
  },
  radiusAxis: {
    type: 'category',
    data: ['a', 'b', 'c', 'd']
  },
  tooltip: {},
  series: {
    type: 'bar',
    data: [2, 1.2, 2.4, 3.6],
    coordinateSystem: 'polar',
    label: {
      show: true,
      position: 'middle',
      formatter: '{b}: {c}'
    }
  }
};
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
