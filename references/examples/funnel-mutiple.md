# funnel-mutiple

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=funnel-mutiple
**Chart Type:** `funnel`

## User Data Requirements

Columns needed: need **stage** + **count** columns

## Data Arrays — Replacement Guide

The code contains **5 data array(s)** to replace:

### data[0]: `legend`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Show', 'Click', 'Visit', 'Inquiry', 'Order']`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `series[0]`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
        { value: 60, name: 'Visit' },
        { value: 30, name: 'Inquiry' },
        { valu...`
- **Replace with**: real data from DuckDB in the same format

### data[2]: `unknown`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
        { value: 60, name: 'Visit' },
        { value: 30, name: 'Inquiry' },
        { valu...`
- **Replace with**: real data from DuckDB in the same format

### data[3]: `unknown`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
        { value: 60, name: 'Visit' },
        { value: 30, name: 'Inquiry' },
        { valu...`
- **Replace with**: real data from DuckDB in the same format

### data[4]: `unknown`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
        { value: 60, name: 'Visit' },
        { value: 30, name: 'Inquiry' },
        { valu...`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Multiple Funnels
category: funnel
titleCN: 多漏斗图
*/
option = {
  title: {
    text: 'Funnel',
    left: 'left',
    top: 'bottom'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b} : {c}%'
  },
  toolbox: {
    orient: 'vertical',
    top: 'center',
    feature: {
      dataView: { readOnly: false },
      restore: {},
      saveAsImage: {}
    }
  },
  legend: {
    orient: 'vertical',
    left: 'left',
    data: ['Show', 'Click', 'Visit', 'Inquiry', 'Order']
  },
  series: [
    {
      name: 'Funnel',
      type: 'funnel',
      width: '40%',
      height: '45%',
      left: '5%',
      top: '50%',
      data: [
        { value: 60, name: 'Visit' },
        { value: 30, name: 'Inquiry' },
        { value: 10, name: 'Order' },
        { value: 80, name: 'Click' },
        { value: 100, name: 'Show' }
      ]
    },
    {
      name: 'Pyramid',
      type: 'funnel',
      width: '40%',
      height: '45%',
      left: '5%',
      top: '5%',
      sort: 'ascending',
      data: [
        { value: 60, name: 'Visit' },
        { value: 30, name: 'Inquiry' },
        { value: 10, name: 'Order' },
        { value: 80, name: 'Click' },
        { value: 100, name: 'Show' }
      ]
    },
    {
      name: 'Funnel',
      type: 'funnel',
      width: '40%',
      height: '45%',
      left: '55%',
      top: '5%',
      label: {
        position: 'left'
      },
      data: [
        { value: 60, name: 'Visit' },
        { value: 30, name: 'Inquiry' },
        { value: 10, name: 'Order' },
        { value: 80, name: 'Click' },
        { value: 100, name: 'Show' }
      ]
    },
    {
      name: 'Pyramid',
      type: 'funnel',
      width: '40%',
      height: '45%',
      left: '55%',
      top: '50%',
      sort: 'ascending',
      label: {
        position: 'left'
      },
      data: [
        { value: 60, name: 'Visit' },
        { value: 30, name: 'Inquiry' },
        { value: 10, name: 'Order' },
        { value: 80, name: 'Click' },
        { value: 100, name: 'Show' }
      ]
    }
  ]
};
```
