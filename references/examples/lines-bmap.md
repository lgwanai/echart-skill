# lines-bmap

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=lines-bmap
**Chart Type:** `lines`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `hangzhou-tracks.json`:

```json
[
  [
    {
      "coord": [
        120.14322240845,
        30.236064370321
      ],
      "elevation": 21
    },
    {
      "coord": [
        120.14280555506,
        30.23633761213
      ],
      "elevation": 5
    },
    {
      "coord": [
        120.14307598649,
        30.236125905084
      ],
      "elevation": 30.7
    },
    {
      "coord": [
        120.14301682797,
        30.236035316745
      ],
      "elevation": 15.4
    },
    {
      "coord": [
        120.1428734612,
     
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
title: A Hiking Trail in Hangzhou - Baidu Map
category: 'map, lines'
tags: bmap
noExplore: true
titleCN: 杭州热门步行路线 - 百度地图
*/
$.get(ROOT_PATH + '/data/asset/data/hangzhou-tracks.json', function (data) {
  const lines = data.map(function (track) {
    return {
      coords: track.map(function (seg, idx) {
        return seg.coord;
      })
    };
  });
  myChart.setOption(
    (option = {
      backgroundColor: 'transparent',
      bmap: {
        center: [120.13066322374, 30.240018034923],
        zoom: 14,
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
          data: lines,
          polyline: true,
          lineStyle: {
            color: 'purple',
            opacity: 0.6,
            width: 1
          }
        }
      ]
    })
  );
});
```
