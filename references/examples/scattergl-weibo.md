# scattergl-weibo

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scattergl-weibo
**Chart Type:** `scatterGL`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Complete Replacement Guide

**1 array(s)** to replace with real data:

### [0] `data` (context: legend)
```
data: ['å¼º', 'ä¸­', 'å¼±']
```

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: å¾®åç­¾å°æ°æ®ç¹äº®ä¸­å½
category: scatterGL
theme: dark
titleCN: å¾®åç­¾å°æ°æ®ç¹äº®ä¸­å½
*/
$.getJSON(ROOT_PATH + '/data/asset/data/weibo.json', function (weiboData) {
  weiboData = weiboData.map(function (serieData, idx) {
    var px = serieData[0] / 1000;
    var py = serieData[1] / 1000;
    var res = [[px, py]];
    for (var i = 2; i < serieData.length; i += 2) {
      var dx = serieData[i] / 1000;
      var dy = serieData[i + 1] / 1000;
      var x = px + dx;
      var y = py + dy;
      res.push([x.toFixed(2), y.toFixed(2), 1]);
      px = x;
      py = y;
    }
    return res;
  });
  myChart.setOption(
    (option = {
      title: {
        text: 'å¾®åç­¾å°æ°æ®ç¹äº®ä¸­å½',
        subtext: 'From ThinkGIS',
        sublink: 'http://www.thinkgis.cn/public/sina',
        left: 'center',
        top: 'top',
        textStyle: {
          color: '#fff'
        }
      },
      tooltip: {},
      legend: {
        left: 'left',
        data: ['å¼º', 'ä¸­', 'å¼±'],
        textStyle: {
          color: '#ccc'
        }
      },
      geo: {
        map: 'china',
        roam: true,
        label: {
          emphasis: {
            show: false
          }
        },
        itemStyle: {
          normal: {
            areaColor: '#323c48',
            borderColor: '#111'
          },
          emphasis: {
            areaColor: '#2a333d'
          }
        }
      },
      series: [
        {
          name: 'å¼±',
          type: 'scatterGL',
          coordinateSystem: 'geo',
          symbolSize: 1,
          itemStyle: {
            shadowBlur: 2,
            shadowColor: 'rgba(37, 140, 249, 0.8)',
            color: 'rgba(37, 140, 249, 0.8)'
          },
          data: weiboData[0]
        },
        {
          name: 'ä¸­',
          type: 'scatterGL',
          coordinateSystem: 'geo',
          symbolSize: 1,
          itemStyle: {
            shadowBlur: 2,
            shadowColor: 'rgba(14, 241, 242, 0.8)',
            color: 'rgba(14, 241, 242, 0.8)'
          },
          data: weiboData[1]
        },
        {
          name: 'å¼º',
          type: 'scatterGL',
          coordinateSystem: 'geo',
          symbolSize: 1,
          itemStyle: {
            shadowBlur: 2,
            shadowColor: 'rgba(255, 255, 255, 0.8)',
            color: 'rgba(255, 255, 255, 0.8)'
          },
          data: weiboData[2]
        }
      ]
    })
  );
});
```
