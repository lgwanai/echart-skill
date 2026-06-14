# data-transform-filter

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=data-transform-filter
**Chart Type:** `filter`

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
title: Data Transform Filter
category: line
titleCN: 数据过滤
difficulty: 3
*/
$.get(
  ROOT_PATH + '/data/asset/data/life-expectancy-table.json',
  function (_rawData) {
    run(_rawData);
  }
);
function run(_rawData) {
  option = {
    dataset: [
      {
        id: 'dataset_raw',
        source: _rawData
      },
      {
        id: 'dataset_since_1950_of_germany',
        fromDatasetId: 'dataset_raw',
        transform: {
          type: 'filter',
          config: {
            and: [
              { dimension: 'Year', gte: 1950 },
              { dimension: 'Country', '=': 'Germany' }
            ]
          }
        }
      },
      {
        id: 'dataset_since_1950_of_france',
        fromDatasetId: 'dataset_raw',
        transform: {
          type: 'filter',
          config: {
            and: [
              { dimension: 'Year', gte: 1950 },
              { dimension: 'Country', '=': 'France' }
            ]
          }
        }
      }
    ],
    title: {
      text: 'Income of Germany and France since 1950'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      nameLocation: 'middle'
    },
    yAxis: {
      name: 'Income'
    },
    series: [
      {
        type: 'line',
        datasetId: 'dataset_since_1950_of_germany',
        showSymbol: false,
        encode: {
          x: 'Year',
          y: 'Income',
          itemName: 'Year',
          tooltip: ['Income']
        }
      },
      {
        type: 'line',
        datasetId: 'dataset_since_1950_of_france',
        showSymbol: false,
        encode: {
          x: 'Year',
          y: 'Income',
          itemName: 'Year',
          tooltip: ['Income']
        }
      }
    ]
  };
  myChart.setOption(option);
}
```
