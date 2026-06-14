# scatter-jitter

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-jitter
**Chart Type:** `category`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

Data arrays to replace: **1**

## Reference Code

```javascript
/*
title: Scatter with Jittering
category: scatter
titleCN: 带抖动的散点图
difficulty: 3
since: 6.0.0
*/
const grid = {
  left: 80,
  right: 50
};
const width = myChart.getWidth() - grid.left - grid.right;
const data = [];
for (let day = 0; day < 7; ++day) {
  for (let i = 0; i < 1000; ++i) {
    const y = Math.tan(i) / 2 + 7;
    data.push([day, y, Math.random()]);
  }
}
option = {
  title: {
    text: 'Scatter with Jittering'
  },
  grid,
  xAxis: {
    type: 'category',
    jitter: (width / 7) * 0.8,
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value',
    max: 10,
    min: 0
  },
  series: [
    {
      name: 'Sleeping Hours',
      type: 'scatter',
      data,
      colorBy: 'data',
      itemStyle: {
        opacity: 0.4
      }
    }
  ]
};
```
