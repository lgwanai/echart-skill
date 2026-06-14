# bar-y-category

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-y-category

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

**3 data arrays** to replace:
- `data[0]`: `data: ['Brazil', 'Indonesia', 'USA', 'India', 'China', 'World']`
- `data[1]`: `data: [18203, 23489, 29034, 104970, 131744, 630230]`
- `data[2]`: `data: [19325, 23438, 31000, 121594, 134141, 681807]`

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: World Population
category: bar
titleCN: 世界人口总量 - 条形图
difficulty: 2
*/
option = {
  title: {
    text: 'World Population'
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {},
  xAxis: {
    type: 'value',
    boundaryGap: [0, 0.01]
  },
  yAxis: {
    type: 'category',
    data: ['Brazil', 'Indonesia', 'USA', 'India', 'China', 'World']
  },
  series: [
    {
      name: '2011',
      type: 'bar',
      data: [18203, 23489, 29034, 104970, 131744, 630230]
    },
    {
      name: '2012',
      type: 'bar',
      data: [19325, 23438, 31000, 121594, 134141, 681807]
    }
  ]
};
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
