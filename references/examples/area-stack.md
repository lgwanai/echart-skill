# area-stack

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=area-stack
**Chart Type:** `cross`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **7 data array(s)** to replace:

### data[0]: `legend`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Email', 'Union Ads', 'Video Ads', 'Direct', 'Search Engine']`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `toolbox`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']`
- **Replace with**: real data from DuckDB in the same format

### data[2]: `series[0]`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [120, 132, 101, 134, 90, 230, 210]`
- **Replace with**: real data from DuckDB in the same format

### data[3]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [220, 182, 191, 234, 290, 330, 310]`
- **Replace with**: real data from DuckDB in the same format

### data[4]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [150, 232, 201, 154, 190, 330, 410]`
- **Replace with**: real data from DuckDB in the same format

### data[5]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [320, 332, 301, 334, 390, 330, 320]`
- **Replace with**: real data from DuckDB in the same format

### data[6]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [820, 932, 901, 934, 1290, 1330, 1320]`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Stacked Area Chart
titleCN: 堆叠面积图
category: line
difficulty: 2
*/
option = {
  title: {
    text: 'Stacked Area Chart'
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross',
      label: {
        backgroundColor: '#6a7985'
      }
    }
  },
  legend: {
    data: ['Email', 'Union Ads', 'Video Ads', 'Direct', 'Search Engine']
  },
  toolbox: {
    feature: {
      saveAsImage: {}
    }
  },
  xAxis: [
    {
      type: 'category',
      boundaryGap: false,
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    }
  ],
  yAxis: [
    {
      type: 'value'
    }
  ],
  series: [
    {
      name: 'Email',
      type: 'line',
      stack: 'Total',
      areaStyle: {},
      emphasis: {
        focus: 'series'
      },
      data: [120, 132, 101, 134, 90, 230, 210]
    },
    {
      name: 'Union Ads',
      type: 'line',
      stack: 'Total',
      areaStyle: {},
      emphasis: {
        focus: 'series'
      },
      data: [220, 182, 191, 234, 290, 330, 310]
    },
    {
      name: 'Video Ads',
      type: 'line',
      stack: 'Total',
      areaStyle: {},
      emphasis: {
        focus: 'series'
      },
      data: [150, 232, 201, 154, 190, 330, 410]
    },
    {
      name: 'Direct',
      type: 'line',
      stack: 'Total',
      areaStyle: {},
      emphasis: {
        focus: 'series'
      },
      data: [320, 332, 301, 334, 390, 330, 320]
    },
    {
      name: 'Search Engine',
      type: 'line',
      stack: 'Total',
      label: {
        show: true,
        position: 'top'
      },
      areaStyle: {},
      emphasis: {
        focus: 'series'
      },
      data: [820, 932, 901, 934, 1290, 1330, 1320]
    }
  ]
};
```
