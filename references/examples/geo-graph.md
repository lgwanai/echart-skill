# geo-graph

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=geo-graph
**Chart Type:** `graph`

## User Data Requirements

Columns needed: need **nodes** [{name,...}] + **links/edges** [{source,target}]

## Data Arrays — Replacement Guide

The code contains **1 data array(s)** to replace:

### data[0]: `series[0]`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
          { name: 'a', value: [7.667821250000001, 46.791734269956265]`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Geo Graph
category: map, graph
titleCN: 地理坐标系上的关系图
difficulty: 3
*/
function createChart() {
  var chRoughLatitude = 47;
  option = {
    title: {
      text: 'Travel Routes'
    },
    geo: {
      map: 'ch',
      roam: true,
      aspectScale: Math.cos((chRoughLatitude * Math.PI) / 180),
      // nameProperty: 'name_en', // If using en name.
      label: {
        show: true,
        textBorderColor: '#fff',
        textBorderWidth: 2
      }
    },
    tooltip: {},
    series: [
      {
        type: 'graph',
        coordinateSystem: 'geo',
        data: [
          { name: 'a', value: [7.667821250000001, 46.791734269956265] },
          { name: 'b', value: [7.404848750000001, 46.516308805996054] },
          { name: 'c', value: [7.376673125000001, 46.24728858538375] },
          { name: 'd', value: [8.015320625000001, 46.39460918238572] },
          { name: 'e', value: [8.616400625, 46.7020608630855] },
          { name: 'f', value: [8.869981250000002, 46.37539345234199] },
          { name: 'g', value: [9.546196250000001, 46.58676648282309] },
          { name: 'h', value: [9.311399375, 47.182454114178896] },
          { name: 'i', value: [9.085994375000002, 47.55395822835779] },
          { name: 'j', value: [8.653968125000002, 47.47709530818285] },
          { name: 'k', value: [8.203158125000002, 47.44506909144329] }
        ],
        edges: [
          {
            source: 'a',
            target: 'b'
          },
          {
            source: 'b',
            target: 'c'
          },
          {
            source: 'c',
            target: 'd'
          },
          {
            source: 'd',
            target: 'e'
          },
          {
            source: 'e',
            target: 'f'
          },
          {
            source: 'f',
            target: 'g'
          },
          {
            source: 'g',
            target: 'h'
          },
          {
            source: 'h',
            target: 'i'
          },
          {
            source: 'i',
            target: 'j'
          },
          {
            source: 'j',
            target: 'k'
          }
        ],
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: 5,
        lineStyle: {
          color: '#718adbff',
          opacity: 1
        }
      }
    ]
  };
  myChart.setOption(option);
}
function fetchGeoJSON() {
  myChart.showLoading();
  $.get(ROOT_PATH + '/data/asset/geo/ch.geo.json', function (geoJSON) {
    echarts.registerMap('ch', geoJSON);
    createChart();
    myChart.hideLoading();
  });
}
fetchGeoJSON();
```
