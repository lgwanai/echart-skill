# bar-data-color

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-data-color
**Chart Type:** `category`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **2 data array(s)** to replace:

### data[0]: `xAxis`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `series[0]`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
        120,
        {
          value: 200,
          itemStyle: {
            color: '#505...`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

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
