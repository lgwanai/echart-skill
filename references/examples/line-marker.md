# line-marker

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-marker
**Chart Type:** `category`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **7 data array(s)** to replace:

### data[0]: `xAxis`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `series[0]`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [10, 11, 13, 11, 12, 12, 9]`
- **Replace with**: real data from DuckDB in the same format

### data[2]: `series[0]`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
          { type: 'max', name: 'Max' },
          { type: 'min', name: 'Min' }
        ]`
- **Replace with**: real data from DuckDB in the same format

### data[3]: `markLine`
- **Format**: `[{name,value},...] — named items`
- **Location**: `data: [{ type: 'average', name: 'Avg' }]`
- **Replace with**: real data from DuckDB in the same format

### data[4]: `markLine`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [1, -2, 2, 5, 3, 2, 0]`
- **Replace with**: real data from DuckDB in the same format

### data[5]: `markLine`
- **Format**: `[{name,value},...] — named items`
- **Location**: `data: [{ name: '周最低', value: -2, xAxis: 1, yAxis: -1.5 }]`
- **Replace with**: real data from DuckDB in the same format

### data[6]: `markLine`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
          { type: 'average', name: 'Avg' },
          [
            {
              symbol: ...`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Temperature Change in the Coming Week
category: line
titleCN: 未来一周气温变化
difficulty: 2
*/
option = {
  title: {
    text: 'Temperature Change in the Coming Week'
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {},
  toolbox: {
    show: true,
    feature: {
      dataZoom: {
        yAxisIndex: 'none'
      },
      dataView: { readOnly: false },
      magicType: { type: ['line', 'bar'] },
      restore: {},
      saveAsImage: {}
    }
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: '{value} °C'
    }
  },
  series: [
    {
      name: 'Highest',
      type: 'line',
      data: [10, 11, 13, 11, 12, 12, 9],
      markPoint: {
        data: [
          { type: 'max', name: 'Max' },
          { type: 'min', name: 'Min' }
        ]
      },
      markLine: {
        data: [{ type: 'average', name: 'Avg' }]
      }
    },
    {
      name: 'Lowest',
      type: 'line',
      data: [1, -2, 2, 5, 3, 2, 0],
      markPoint: {
        data: [{ name: '周最低', value: -2, xAxis: 1, yAxis: -1.5 }]
      },
      markLine: {
        data: [
          { type: 'average', name: 'Avg' },
          [
            {
              symbol: 'none',
              x: '90%',
              yAxis: 'max'
            },
            {
              symbol: 'circle',
              label: {
                position: 'start',
                formatter: 'Max'
              },
              type: 'max',
              name: '最高点'
            }
          ]
        ]
      }
    }
  ]
};
```
