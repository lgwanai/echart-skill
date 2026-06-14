# gauge

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=gauge
**Chart Type:** `gauge`

## User Data Requirements

Columns needed: need a single **value** (aggregate)

## Data Arrays — Replacement Guide

The code contains **1 data array(s)** to replace:

### data[0]: `series[0]`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
        {
          value: 50,
          name: 'SCORE'
        }
      ]`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Gauge Basic chart
titleCN: 基础仪表盘
category: gauge
difficulty: 1
*/
option = {
  tooltip: {
    formatter: '{a} <br/>{b} : {c}%'
  },
  series: [
    {
      name: 'Pressure',
      type: 'gauge',
      detail: {
        formatter: '{value}'
      },
      data: [
        {
          value: 50,
          name: 'SCORE'
        }
      ]
    }
  ]
};
```
