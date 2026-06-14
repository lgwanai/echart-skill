# bar-polar-stack-radial

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-polar-stack-radial
**Chart Type:** `category`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **5 data array(s)** to replace:

### data[0]: `unknown`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `series[0]`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [1, 2, 3, 4, 3, 5, 1]`
- **Replace with**: real data from DuckDB in the same format

### data[2]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [2, 4, 6, 1, 3, 2, 1]`
- **Replace with**: real data from DuckDB in the same format

### data[3]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [1, 2, 3, 4, 1, 2, 5]`
- **Replace with**: real data from DuckDB in the same format

### data[4]: `legend`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['A', 'B', 'C']`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Stacked Bar Chart on Polar(Radial)
titleCN: 极坐标系下的堆叠柱状图
category: bar
difficulty: 7
*/
option = {
  angleAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  radiusAxis: {},
  polar: {},
  series: [
    {
      type: 'bar',
      data: [1, 2, 3, 4, 3, 5, 1],
      coordinateSystem: 'polar',
      name: 'A',
      stack: 'a',
      emphasis: {
        focus: 'series'
      }
    },
    {
      type: 'bar',
      data: [2, 4, 6, 1, 3, 2, 1],
      coordinateSystem: 'polar',
      name: 'B',
      stack: 'a',
      emphasis: {
        focus: 'series'
      }
    },
    {
      type: 'bar',
      data: [1, 2, 3, 4, 1, 2, 5],
      coordinateSystem: 'polar',
      name: 'C',
      stack: 'a',
      emphasis: {
        focus: 'series'
      }
    }
  ],
  legend: {
    show: true,
    data: ['A', 'B', 'C']
  }
};
```
