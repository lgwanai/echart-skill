# map-iceland-pie

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=map-iceland-pie
**Chart Type:** `pie`

## User Data Requirements

Columns needed: need **name** + **value** columns

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `iceland.geo.json`:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -14.6146,
              65.9863
            ],
            [
              -14.663,
              65.9811
            ],
            [
              -14.6941,
              65.9438
            ],
            [
              -15.1014,
              65.922
            ],
            [
              -15.1263,

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
title: Pie Charts on GEO Map
category: map, pie
titleCN: 在地图上显示饼图
since: 5.4.0
difficulty: 5
*/
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/geo/iceland.geo.json', function (geoJSON) {
  echarts.registerMap('iceland', geoJSON);
  function randomPieSeries(center, radius) {
    const data = ['A', 'B', 'C', 'D'].map((t) => {
      return {
        value: Math.round(Math.random() * 100),
        name: 'Category ' + t
      };
    });
    return {
      type: 'pie',
      coordinateSystem: 'geo',
      tooltip: {
        formatter: '{b}: {c} ({d}%)'
      },
      label: {
        show: false
      },
      labelLine: {
        show: false
      },
      animationDuration: 0,
      radius,
      center,
      data
    };
  }
  option = {
    geo: {
      map: 'iceland',
      roam: true,
      aspectScale: Math.cos((65 * Math.PI) / 180),
      // nameProperty: 'name_en', // If using en name.
      itemStyle: {
        areaColor: '#e7e8ea'
      },
      emphasis: {
        label: { show: false }
      }
    },
    tooltip: {},
    legend: {},
    series: [
      randomPieSeries([-19.007740346534653, 64.1780281585128], 45),
      randomPieSeries([-17.204666089108912, 65.44804833928391], 25),
      randomPieSeries([-15.264995297029705, 64.8592208009264], 30),
      randomPieSeries(
        // it's also supported to use geo region name as center since v5.4.1
        +echarts.version.split('.').slice(0, 3).join('') > 540
          ? 'Vestfirðir'
          : // or you can only use the LngLat array
            [-13, 66],
        30
      )
    ]
  };
  myChart.hideLoading();
  myChart.setOption(option);
});
```
