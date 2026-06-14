# bar-y-category-stack

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-y-category-stack
**Chart Type:** `shadow`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **6 data array(s)** to replace:

### data[0]: `legend`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `series[0]`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [320, 302, 301, 334, 390, 330, 320]`
- **Replace with**: real data from DuckDB in the same format

### data[2]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [120, 132, 101, 134, 90, 230, 210]`
- **Replace with**: real data from DuckDB in the same format

### data[3]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [220, 182, 191, 234, 290, 330, 310]`
- **Replace with**: real data from DuckDB in the same format

### data[4]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [150, 212, 201, 154, 190, 330, 410]`
- **Replace with**: real data from DuckDB in the same format

### data[5]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [820, 832, 901, 934, 1290, 1330, 1320]`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Stacked Horizontal Bar
titleCN: 堆叠条形图
category: bar
difficulty: 3
*/
option = {
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      // Use axis to trigger tooltip
      type: 'shadow' // 'shadow' as default; can also be 'line' or 'shadow'
    }
  },
  legend: {},
  xAxis: {
    type: 'value'
  },
  yAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  series: [
    {
      name: 'Direct',
      type: 'bar',
      stack: 'total',
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: [320, 302, 301, 334, 390, 330, 320]
    },
    {
      name: 'Mail Ad',
      type: 'bar',
      stack: 'total',
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: [120, 132, 101, 134, 90, 230, 210]
    },
    {
      name: 'Affiliate Ad',
      type: 'bar',
      stack: 'total',
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: [220, 182, 191, 234, 290, 330, 310]
    },
    {
      name: 'Video Ad',
      type: 'bar',
      stack: 'total',
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: [150, 212, 201, 154, 190, 330, 410]
    },
    {
      name: 'Search Engine',
      type: 'bar',
      stack: 'total',
      label: {
        show: true
      },
      emphasis: {
        focus: 'series'
      },
      data: [820, 832, 901, 934, 1290, 1330, 1320]
    }
  ]
};
```
