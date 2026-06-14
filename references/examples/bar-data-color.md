# bar-data-color

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-data-color

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

**2 data arrays** to replace:
- `data[0]`: `data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']`
- `data[1]`: `data: [
        120,
        {
          value: 200,
          itemStyle: {
    ...`

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Set Style of Single Bar.
category: bar
titleCN: 自定义单个柱子颜色
difficulty: 1
*/
option = {
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [
        120,
        {
          value: 200,
          itemStyle: {
            color: '#505372'
          }
        },
        150,
        80,
        70,
        110,
        130
      ],
      type: 'bar'
    }
  ]
};
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
