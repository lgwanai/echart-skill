# candlestick-simple

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=candlestick-simple
**Chart Type:** `candlestick`

## User Data Requirements

Columns needed: need **open/close/low/high** columns

## Data Arrays — Complete Replacement Guide

**2 array(s)** to replace with real data:

### [0] `data` (context: xAxis)
```
data: ['2017-10-24', '2017-10-25', '2017-10-26', '2017-10-27']
```

### [1] `data` (context: series)
```
data: [
        [20, 34, 10, 38],
        [40, 35, 30, 50],
        [31, 38, 33, 44],
        [38, 15, 5, 42]
      ]
```

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Basic Candlestick
category: candlestick
titleCN: 基础 K 线图
difficulty: 0
*/
option = {
  xAxis: {
    data: ['2017-10-24', '2017-10-25', '2017-10-26', '2017-10-27']
  },
  yAxis: {},
  series: [
    {
      type: 'candlestick',
      data: [
        [20, 34, 10, 38],
        [40, 35, 30, 50],
        [31, 38, 33, 44],
        [38, 15, 5, 42]
      ]
    }
  ]
};
```
