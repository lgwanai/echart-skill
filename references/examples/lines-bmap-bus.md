# lines-bmap-bus

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=lines-bmap-bus
**Chart Type:** `lines`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `lines-bus.json`:

```json
[
  [
    1164383,
    401471,
    -11,
    -13,
    1,
    -49,
    -26,
    -14,
    99,
    -170,
    4,
    -36,
    87,
    -2,
    16,
    -141,
    -2,
    -15,
    -47,
    -6,
    -168,
    -9,
    -2,
    22,
    -74,
    -4,
    -138,
    10,
    12,
    -152,
    9,
    -55,
    -17,
    -111,
    13,
    -176,
    -20,
    -38,
    1,
    -57,
    31,
    -54,
    28,
    -85,
    -5,
    -126,
    -13,
    -62,
    1,
    -34,
    -84,
    1,
    -3,
    -218,
    15,
    6,
    78
...
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
title: Bus Lines of Beijing - Baidu Map
category: 'map, lines'
noExplore: true
tags: bmap
titleCN: 北京公交路线 - 百度地图
*/
$.get(ROOT_PATH + '/data/asset/data/lines-bus.json', function (data) {
  let busLines = [].concat.apply(
    [],
    data.map(function (busLine, idx) {
      let prevPt = [];
      let points = [];
      for (let i = 0; i < busLine.length; i += 2) {
        let pt = [busLine[i], busLine[i + 1]];
        if (i > 0) {
          pt = [prevPt[0] + pt[0], prevPt[1] + pt[1]];
        }
        prevPt = pt;
        points.push([pt[0] / 1e4, pt[1] / 1e4]);
      }
      return {
        coords: points
      };
    })
  );
  myChart.setOption(
    (option = {
      backgroundColor: 'transparent',
      bmap: {
        center: [116.46, 39.92],
        zoom: 10,
        roam: true,
        mapStyle: {
          styleJson: [
            {
              featureType: 'water',
              elementType: 'all',
              stylers: {
                color: '#d1d1d1'
              }
            },
            {
              featureType: 'land',
              elementType: 'all',
              stylers: {
                color: '#f3f3f3'
              }
            },
            {
              featureType: 'railway',
              elementType: 'all',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'highway',
              elementType: 'all',
              stylers: {
                color: '#fdfdfd'
              }
            },
            {
              featureType: 'highway',
              elementType: 'labels',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'arterial',
              elementType: 'geometry',
              stylers: {
                color: '#fefefe'
              }
            },
            {
              featureType: 'arterial',
              elementType: 'geometry.fill',
              stylers: {
                color: '#fefefe'
              }
            },
            {
              featureType: 'poi',
              elementType: 'all',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'green',
              elementType: 'all',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'subway',
              elementType: 'all',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'manmade',
              elementType: 'all',
              stylers: {
                color: '#d1d1d1'
              }
            },
            {
              featureType: 'local',
              elementType: 'all',
              stylers: {
                color: '#d1d1d1'
              }
            },
            {
              featureType: 'arterial',
              elementType: 'labels',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'boundary',
              elementType: 'all',
              stylers: {
                color: '#fefefe'
              }
            },
            {
              featureType: 'building',
              elementType: 'all',
              stylers: {
                color: '#d1d1d1'
              }
            },
            {
              featureType: 'label',
              elementType: 'labels.text.fill',
              stylers: {
                color: '#999999'
              }
            }
          ]
        }
      },
      series: [
        {
          type: 'lines',
          coordinateSystem: 'bmap',
          polyline: true,
          data: busLines,
          silent: true,
          lineStyle: {
            color: 'rgb(200, 35, 45)',
            opacity: 0.2,
            width: 1
          },
          progressiveThreshold: 500,
          progressive: 200
        }
      ]
    })
  );
});
```
