# geo-choropleth-scatter

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=geo-choropleth-scatter
**Chart Type:** `scatter`

## User Data Requirements

Columns needed: need **x** + **y** columns (both numeric)

## Data Arrays — Replacement Guide

The code contains **2 data array(s)** to replace:

### data[0]: `series`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [
          [-21.9348415, 64.1334671, 14523]`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `series`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
          { name: 'Austurland', value: 423 },
          { name: 'Suðurland', value: 256 },
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
title: Geo Choropleth and Scatter
category: map, scatter
titleCN: 地理坐标系上的等值区划图和散点图
difficulty: 5
*/
function createChart() {
  var icelandRoughLatitude = 65;
  option = {
    geo: {
      map: 'iceland',
      roam: true,
      aspectScale: Math.cos((icelandRoughLatitude * Math.PI) / 180),
      // nameProperty: 'name_en', // If using en name.
      label: {
        show: true,
        color: '#555'
      }
    },
    tooltip: {},
    visualMap: [
      {
        orient: 'horizontal',
        calculable: true,
        right: 0,
        bottom: 0,
        seriesIndex: 0,
        // min/max is specified as series.data value extent.
        min: 0,
        max: 1e5,
        dimension: 2,
        inRange: {
          symbolSize: [5, 30]
        },
        controller: {
          inRange: {
            color: ['#66c2a5']
          }
        }
      },
      {
        orient: 'horizontal',
        calculable: true,
        left: 0,
        bottom: 0,
        seriesIndex: 1,
        // min/max is specified as series.data value extent.
        min: 0,
        max: 1e3,
        dimension: 0,
        inRange: {
          color: ['#deebf7', '#3182bd']
        }
      }
    ],
    series: [
      {
        type: 'scatter',
        coordinateSystem: 'geo',
        geoIndex: 0,
        encode: {
          // `2` is the dimension index of series.data
          tooltip: 2,
          label: 2
        },
        data: [
          [-21.9348415, 64.1334671, 14523],
          [-19.028531, 63.710241, 45126],
          [-17.089925, 65.37887072, 12345],
          [-19.15936, 65.6218101, 56789],
          [-19.849175, 65.7287035, 67890],
          [-23.18326, 65.582939, 89012],
          [-14.9515, 64.475135, 34567],
          [-20.88389, 63.85321, 45678]
        ],
        itemStyle: {
          color: '#66c2a5',
          borderWidth: 1,
          borderColor: '#3c7865'
        }
      },
      {
        // Effectively this is a choropleth map.
        type: 'map',
        // Specify geoIndex to share the geo component with the scatter series above,
        // instead of creating an internal geo coord sys.
        geoIndex: 0,
        map: '',
        data: [
          { name: 'Austurland', value: 423 },
          { name: 'Suðurland', value: 256 },
          { name: 'Norðurland vestra', value: 489 },
          { name: 'Norðurland eystra', value: 51 }
        ]
      }
    ]
  };
  myChart.setOption(option);
}
function fetchGeoJSON() {
  myChart.showLoading();
  $.get(ROOT_PATH + '/data/asset/geo/iceland.geo.json', function (geoJSON) {
    echarts.registerMap('iceland', geoJSON);
    createChart();
    myChart.hideLoading();
  });
}
fetchGeoJSON();
```
