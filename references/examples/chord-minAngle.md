# chord-minAngle

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=chord-minAngle
**Chart Type:** `chord`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **1 data array(s)** to replace:

### data[0]: `series[0]`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
        { name: 'A' },
        { name: 'B' },
        { name: 'C' },
        { name: 'D' },
...`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Chord minAngle
category: chord
titleCN: 和弦图 minAngle
difficulty: 1
since: 6.0.0
*/
option = {
  tooltip: {},
  legend: {},
  series: [
    {
      type: 'chord',
      label: { show: true },
      minAngle: 30,
      data: [
        { name: 'A' },
        { name: 'B' },
        { name: 'C' },
        { name: 'D' },
        { name: 'E' },
        { name: 'F' }
      ],
      links: [
        { source: 'A', target: 'B', value: 40 },
        { source: 'B', target: 'C', value: 20 },
        { source: 'E', target: 'A', value: 5 }
      ]
    }
  ]
};
```
