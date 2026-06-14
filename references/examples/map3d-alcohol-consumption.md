# map3d-alcohol-consumption

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=map3d-alcohol-consumption
**Chart Type:** `map3D`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Map3D - Alcohol Consumption
category: map3D
titleCN: Map3D - Alcohol Consumption
*/
$.getJSON(ROOT_PATH + '/data-gl/asset/data/alcohol.json', function (data) {
  var regionData = data.map(function (item) {
    return {
      name: item[0],
      value: item[1]
    };
  });
  console.log(regionData);
  myChart.setOption({
    backgroundColor: '#cdcfd5',
    visualMap: {
      min: 0,
      max: 15,
      realtime: true,
      calculable: true,
      inRange: {
        color: [
          '#313695',
          '#4575b4',
          '#74add1',
          '#abd9e9',
          '#e0f3f8',
          '#ffffbf',
          '#fee090',
          '#fdae61',
          '#f46d43',
          '#d73027',
          '#a50026'
        ]
      }
    },
    series: [
      {
        type: 'map3D',
        map: 'world',
        shading: 'lambert',
        realisticMaterial: {
          roughness: 0.2,
          metalness: 0
        },
        postEffect: {
          enable: true,
          SSAO: {
            enable: true,
            radius: 2,
            intensity: 1
          }
        },
        groundPlane: {
          show: true
        },
        light: {
          main: {
            intensity: 2,
            shadow: true,
            shadowQuality: 'high',
            alpha: 30
          },
          ambient: {
            intensity: 0
          },
          ambientCubemap: {
            texture: ROOT_PATH + '/data-gl/asset/canyon.hdr',
            exposure: 1,
            diffuseIntensity: 1
          }
        },
        viewControl: {
          distance: 50
        },
        regionHeight: 1,
        data: regionData
      }
    ]
  });
});
```
