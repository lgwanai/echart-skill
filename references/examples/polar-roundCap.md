# polar-roundCap

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=polar-roundCap
**Chart Type:** `category`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **4 data array(s)** to replace:

### data[0]: `unknown`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['v', 'w', 'x', 'y', 'z']`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `series[0]`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [4, 3, 2, 1, 0]`
- **Replace with**: real data from DuckDB in the same format

### data[2]: `unknown`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [4, 3, 2, 1, 0]`
- **Replace with**: real data from DuckDB in the same format

### data[3]: `legend`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Without Round Cap', 'With Round Cap']`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Rounded Bar on Polar
category: bar
titleCN: 圆角环形图
difficulty: 7
*/
option = {
  angleAxis: {
    max: 2,
    startAngle: 30,
    splitLine: {
      show: false
    }
  },
  radiusAxis: {
    type: 'category',
    data: ['v', 'w', 'x', 'y', 'z'],
    z: 10
  },
  polar: {},
  series: [
    {
      type: 'bar',
      data: [4, 3, 2, 1, 0],
      coordinateSystem: 'polar',
      name: 'Without Round Cap',
      itemStyle: {
        borderColor: 'red',
        opacity: 0.8,
        borderWidth: 1
      }
    },
    {
      type: 'bar',
      data: [4, 3, 2, 1, 0],
      coordinateSystem: 'polar',
      name: 'With Round Cap',
      roundCap: true,
      itemStyle: {
        borderColor: 'green',
        opacity: 0.8,
        borderWidth: 1
      }
    }
  ],
  legend: {
    show: true,
    data: ['Without Round Cap', 'With Round Cap']
  }
};
```
