# scatter3d-scatter

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter3d-scatter
**Chart Type:** `value`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `life-expectancy-table.json`:

```json
[
  [
    "Income",
    "Life Expectancy",
    "Population",
    "Country",
    "Year"
  ],
  [
    815,
    34.05,
    351014,
    "Australia",
    1800
  ],
  [
    1314,
    39,
    645526,
    "Canada",
    1800
  ]
]
```

Agent: build DuckDB query to produce matching data structure.
## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: 3D Scatter with Scatter Matrix
category: scatter3D
titleCN: ä¸ç»´æ£ç¹å¾åæ£ç¹ç©éµç»åä½¿ç¨
*/
$.get(
  ROOT_PATH + '/data/asset/data/life-expectancy-table.json',
  function (data) {
    var sizeValue = '57%';
    var symbolSize = 2.5;
    option = {
      tooltip: {},
      grid3D: {
        width: '50%'
      },
      xAxis3D: {},
      yAxis3D: {},
      zAxis3D: {},
      grid: [
        { left: '50%', width: '20%', bottom: sizeValue },
        { left: '75%', width: '20%', bottom: sizeValue },
        { left: '50%', width: '20%', top: sizeValue },
        { left: '75%', width: '20%', top: sizeValue }
      ],
      xAxis: [
        {
          type: 'value',
          gridIndex: 0,
          name: 'Income',
          axisLabel: { rotate: 50, interval: 0 }
        },
        {
          type: 'category',
          gridIndex: 1,
          name: 'Country',
          boundaryGap: false,
          axisLabel: { rotate: 50, interval: 0 }
        },
        {
          type: 'value',
          gridIndex: 2,
          name: 'Income',
          axisLabel: { rotate: 50, interval: 0 }
        },
        {
          type: 'value',
          gridIndex: 3,
          name: 'Life Expectancy',
          axisLabel: { rotate: 50, interval: 0 }
        }
      ],
      yAxis: [
        { type: 'value', gridIndex: 0, name: 'Life Expectancy' },
        { type: 'value', gridIndex: 1, name: 'Income' },
        { type: 'value', gridIndex: 2, name: 'Population' },
        { type: 'value', gridIndex: 3, name: 'Population' }
      ],
      dataset: {
        dimensions: [
          'Income',
          'Life Expectancy',
          'Population',
          'Country',
          { name: 'Year', type: 'ordinal' }
        ],
        source: data
      },
      series: [
        {
          type: 'scatter3D',
          symbolSize: 3,
          encode: {
            x: 'Population',
            y: 'Life Expectancy',
            z: 'Income',
            tooltip: [0, 1, 2, 3, 4]
          }
        },
        {
          type: 'scatter',
          symbolSize: symbolSize,
          xAxisIndex: 0,
          yAxisIndex: 0,
          encode: {
            x: 'Income',
            y: 'Life Expectancy',
            tooltip: [0, 1, 2, 3, 4]
          }
        },
        {
          type: 'scatter',
          symbolSize: symbolSize,
          xAxisIndex: 1,
          yAxisIndex: 1,
          encode: {
            x: 'Country',
            y: 'Income',
            tooltip: [0, 1, 2, 3, 4]
          }
        },
        {
          type: 'scatter',
          symbolSize: symbolSize,
          xAxisIndex: 2,
          yAxisIndex: 2,
          encode: {
            x: 'Income',
            y: 'Population',
            tooltip: [0, 1, 2, 3, 4]
          }
        },
        {
          type: 'scatter',
          symbolSize: symbolSize,
          xAxisIndex: 3,
          yAxisIndex: 3,
          encode: {
            x: 'Life Expectancy',
            y: 'Population',
            tooltip: [0, 1, 2, 3, 4]
          }
        }
      ]
    };
    myChart.setOption(option);
  }
);
```
