# bar-stack

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-stack
**Chart Type:** `shadow`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **11 data array(s)** to replace:

### data[0]: `legend`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `series[0]`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [320, 332, 301, 334, 390, 330, 320]`
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
- **Location**: `data: [150, 232, 201, 154, 190, 330, 410]`
- **Replace with**: real data from DuckDB in the same format

### data[5]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [862, 1018, 964, 1026, 1679, 1600, 1570]`
- **Replace with**: real data from DuckDB in the same format

### data[6]: `markLine`
- **Format**: `[[x,y],...] — XY pairs`
- **Location**: `data: [[{ type: 'min' }, { type: 'max' }]`
- **Replace with**: real data from DuckDB in the same format

### data[7]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [620, 732, 701, 734, 1090, 1130, 1120]`
- **Replace with**: real data from DuckDB in the same format

### data[8]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [120, 132, 101, 134, 290, 230, 220]`
- **Replace with**: real data from DuckDB in the same format

### data[9]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [60, 72, 71, 74, 190, 130, 110]`
- **Replace with**: real data from DuckDB in the same format

### data[10]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [62, 82, 91, 84, 109, 110, 120]`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Stacked Column Chart
titleCN: 堆叠柱状图
category: bar
difficulty: 3
*/
option = {
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {},
  xAxis: [
    {
      type: 'category',
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
      name: 'Direct',
      type: 'bar',
      emphasis: {
        focus: 'series'
      },
      data: [320, 332, 301, 334, 390, 330, 320]
    },
    {
      name: 'Email',
      type: 'bar',
      stack: 'Ad',
      emphasis: {
        focus: 'series'
      },
      data: [120, 132, 101, 134, 90, 230, 210]
    },
    {
      name: 'Union Ads',
      type: 'bar',
      stack: 'Ad',
      emphasis: {
        focus: 'series'
      },
      data: [220, 182, 191, 234, 290, 330, 310]
    },
    {
      name: 'Video Ads',
      type: 'bar',
      stack: 'Ad',
      emphasis: {
        focus: 'series'
      },
      data: [150, 232, 201, 154, 190, 330, 410]
    },
    {
      name: 'Search Engine',
      type: 'bar',
      data: [862, 1018, 964, 1026, 1679, 1600, 1570],
      emphasis: {
        focus: 'series'
      },
      markLine: {
        lineStyle: {
          type: 'dashed'
        },
        data: [[{ type: 'min' }, { type: 'max' }]]
      }
    },
    {
      name: 'Baidu',
      type: 'bar',
      barWidth: 5,
      stack: 'Search Engine',
      emphasis: {
        focus: 'series'
      },
      data: [620, 732, 701, 734, 1090, 1130, 1120]
    },
    {
      name: 'Google',
      type: 'bar',
      stack: 'Search Engine',
      emphasis: {
        focus: 'series'
      },
      data: [120, 132, 101, 134, 290, 230, 220]
    },
    {
      name: 'Bing',
      type: 'bar',
      stack: 'Search Engine',
      emphasis: {
        focus: 'series'
      },
      data: [60, 72, 71, 74, 190, 130, 110]
    },
    {
      name: 'Others',
      type: 'bar',
      stack: 'Search Engine',
      emphasis: {
        focus: 'series'
      },
      data: [62, 82, 91, 84, 109, 110, 120]
    }
  ]
};
```
