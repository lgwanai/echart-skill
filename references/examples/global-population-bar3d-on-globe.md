# global-population-bar3d-on-globe

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=global-population-bar3d-on-globe
**Chart Type:** `bar3D`

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
title: Global Population - Bar3D on Globe
category: bar3D
titleCN: å¨çäººå£åå¸ - å°çä¸ç Bar3D
*/
$.getJSON(ROOT_PATH + '/data-gl/asset/data/population.json', function (data) {
  data = data
    .filter(function (dataItem) {
      return dataItem[2] > 0;
    })
    .map(function (dataItem) {
      return [dataItem[0], dataItem[1], Math.sqrt(dataItem[2])];
    });
  option = {
    backgroundColor: '#000',
    globe: {
      baseTexture: ROOT_PATH + '/data-gl/asset/world.topo.bathy.200401.jpg',
      heightTexture: ROOT_PATH + '/data-gl/asset/world.topo.bathy.200401.jpg',
      shading: 'lambert',
      environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
      light: {
        main: {
          intensity: 2
        }
      },
      viewControl: {
        autoRotate: false
      }
    },
    visualMap: {
      max: 40,
      calculable: true,
      realtime: false,
      inRange: {
        colorLightness: [0.2, 0.9]
      },
      textStyle: {
        color: '#fff'
      },
      controller: {
        inRange: {
          color: 'orange'
        }
      },
      outOfRange: {
        colorAlpha: 0
      }
    },
    series: [
      {
        type: 'bar3D',
        coordinateSystem: 'globe',
        data: data,
        barSize: 0.6,
        minHeight: 0.2,
        silent: true,
        itemStyle: {
          color: 'orange'
        }
      }
    ]
  };
  myChart.setOption(option);
});
```
