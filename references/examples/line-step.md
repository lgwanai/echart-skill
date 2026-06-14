# line-step

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-step
**Chart Type:** `category`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **5 data array(s)** to replace:

### data[0]: `legend`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Step Start', 'Step Middle', 'Step End']`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `toolbox`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']`
- **Replace with**: real data from DuckDB in the same format

### data[2]: `series[0]`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [120, 132, 101, 134, 90, 230, 210]`
- **Replace with**: real data from DuckDB in the same format

### data[3]: `unknown`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [220, 282, 201, 234, 290, 430, 410]`
- **Replace with**: real data from DuckDB in the same format

### data[4]: `unknown`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [450, 432, 401, 454, 590, 530, 510]`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Step Line
category: line
titleCN: 阶梯折线图
difficulty: 7
*/
option = {
  title: {
    text: 'Step Line'
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['Step Start', 'Step Middle', 'Step End']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  toolbox: {
    feature: {
      saveAsImage: {}
    }
  },
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: 'Step Start',
      type: 'line',
      step: 'start',
      data: [120, 132, 101, 134, 90, 230, 210]
    },
    {
      name: 'Step Middle',
      type: 'line',
      step: 'middle',
      data: [220, 282, 201, 234, 290, 430, 410]
    },
    {
      name: 'Step End',
      type: 'line',
      step: 'end',
      data: [450, 432, 401, 454, 590, 530, 510]
    }
  ]
};
```
