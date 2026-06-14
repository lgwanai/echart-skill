# heatmap-bmap

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=heatmap-bmap
**Chart Type:** `heatmap`

## User Data Requirements

Columns needed: need **x**, **y**, **value** columns

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
title: Heatmap on Baidu Map Extension
category: heatmap
tags: bmap
noExplore: true
titleCN: 热力图与百度地图扩展
difficulty: 3
*/
$.get(ROOT_PATH + '/data/asset/data/hangzhou-tracks.json', function (data) {
  var points = [].concat.apply(
    [],
    data.map(function (track) {
      return track.map(function (seg) {
        return seg.coord.concat([1]);
      });
    })
  );
  myChart.setOption(
    (option = {
      animation: false,
      bmap: {
        center: [120.13066322374, 30.240018034923],
        zoom: 14,
        roam: true
      },
      visualMap: {
        show: false,
        top: 'top',
        min: 0,
        max: 5,
        seriesIndex: 0,
        calculable: true,
        inRange: {
          color: ['blue', 'blue', 'green', 'yellow', 'red']
        }
      },
      series: [
        {
          type: 'heatmap',
          coordinateSystem: 'bmap',
          data: points,
          pointSize: 5,
          blurSize: 6
        }
      ]
    })
  );
  // 添加百度地图插件
  var bmap = myChart.getModel().getComponent('bmap').getBMap();
  bmap.addControl(new BMap.MapTypeControl());
});
```
