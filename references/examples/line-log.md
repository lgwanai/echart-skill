# line-log

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-log

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

**4 data arrays** to replace:
- `data[0]`: `data: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']`
- `data[1]`: `data: [1, 3, 9, 27, 81, 247, 741, 2223, 6669]`
- `data[2]`: `data: [1, 2, 4, 8, 16, 32, 64, 128, 256]`
- `data[3]`: `data: [
        1 / 2,
        1 / 4,
        1 / 8,
        1 / 16,
        1 /...`

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Log Axis
category: line
titleCN: 对数轴示例
difficulty: 7
*/
option = {
  title: {
    text: 'Log Axis',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b} : {c}'
  },
  legend: {
    left: 'left'
  },
  xAxis: {
    type: 'category',
    name: 'x',
    splitLine: { show: false },
    data: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  yAxis: {
    type: 'log',
    name: 'y',
    minorSplitLine: {
      show: true
    }
  },
  series: [
    {
      name: 'Log2',
      type: 'line',
      data: [1, 3, 9, 27, 81, 247, 741, 2223, 6669]
    },
    {
      name: 'Log3',
      type: 'line',
      data: [1, 2, 4, 8, 16, 32, 64, 128, 256]
    },
    {
      name: 'Log1/2',
      type: 'line',
      data: [
        1 / 2,
        1 / 4,
        1 / 8,
        1 / 16,
        1 / 32,
        1 / 64,
        1 / 128,
        1 / 256,
        1 / 512
      ]
    }
  ]
};
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
