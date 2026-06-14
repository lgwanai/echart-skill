# scatter3D-dataset

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter3D-dataset
**Chart Type:** `category`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Complete Replacement Guide

**1 array(s)** to replace with real data:

### [0] `dimensions` (context: dataset)
```
dimensions: [
          'Income',
          'Life Expectancy',
          'Population',
          'Country',
          { name: 'Year', type: 'ordinal' ...
```

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: 3D Scatter with Dataset
category: scatter3D
titleCN: ä½¿ç¨ dataset ä¸ºä¸ç»´æ£ç¹å¾è®¾ç½®æ°æ®
*/
$.get(
  ROOT_PATH + '/data/asset/data/life-expectancy-table.json',
  function (data) {
    var symbolSize = 2.5;
    option = {
      grid3D: {},
      xAxis3D: {
        type: 'category'
      },
      yAxis3D: {},
      zAxis3D: {},
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
          symbolSize: symbolSize,
          encode: {
            x: 'Country',
            y: 'Life Expectancy',
            z: 'Income',
            tooltip: [0, 1, 2, 3, 4]
          }
        }
      ]
    };
    myChart.setOption(option);
  }
);
```
