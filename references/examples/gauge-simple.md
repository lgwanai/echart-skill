# gauge-simple

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=gauge-simple
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
title: Simple Gauge
titleCN: 带标签数字动画的基础仪表盘
category: gauge
difficulty: 1
videoStart: 0
videoEnd: 1000
*/
option = {
  tooltip: {
    formatter: '{a} <br/>{b} : {c}%'
  },
  series: [
    {
      name: 'Pressure',
      type: 'gauge',
      progress: {
        show: true
      },
      detail: {
        valueAnimation: true,
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
