# line-in-cartesian-coordinate-system

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-in-cartesian-coordinate-system
**Chart Type:** `line`

## User Data Requirements

Columns needed: need **time/category** + **value** columns

## Data Arrays — Replacement Guide

The code contains **1 data array(s)** to replace:

### data[0]: `series[0]`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [
        [10, 40]`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Line Chart in Cartesian Coordinate System
category: line
titleCN: 双数值轴折线图
difficulty: 7
*/
option = {
  xAxis: {},
  yAxis: {},
  series: [
    {
      data: [
        [10, 40],
        [50, 100],
        [40, 20]
      ],
      type: 'line'
    }
  ]
};
```
