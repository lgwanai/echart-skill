# scatter-weibo

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-weibo
**Chart Type:** `scatter`

## User Data Requirements

Columns needed: need **x** + **y** columns (both numeric)

## Data Arrays — Replacement Guide

The code contains **1 data array(s)** to replace:

### data[0]: `legend`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['强', '中', '弱']`
- **Replace with**: real data from DuckDB in the same format


## External Data Format

This example uses external data. Format from `weibo.json`:

```json
[
  [
    73960,
    39707,
    132,
    102,
    88,
    -34,
    263,
    34,
    0,
    -34,
    88,
    34,
    44,
    202,
    132,
    -169,
    44,
    -1122,
    88,
    -1560,
    44,
    1594,
    0,
    -550,
    44,
    1571,
    0,
    -1124,
    44,
    0,
    0,
    -34,
    0,
    -344,
    0,
    -69,
    44,
    1537,
    0,
    -68,
    44,
    -271,
    0,
    -991,
    0,
    -380,
    87,
    723,
    0,
    -412,
    0,
    -346,
    44,
    895,
    0,
    -377,
    0,
 
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
title: Sign in of weibo
category: scatter
titleCN: 微博签到数据点亮中国
noExplore: true
*/
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/data/weibo.json', function (weiboData) {
  myChart.hideLoading();
  const newWeiboData = weiboData.map(function (serieData, idx) {
    let px = serieData[0] / 1000;
    let py = serieData[1] / 1000;
    let res = [[px, py]];
    for (let i = 2; i < serieData.length; i += 2) {
      let dx = serieData[i] / 1000;
      let dy = serieData[i + 1] / 1000;
      let x = px + dx;
      let y = py + dy;
      res.push([+x.toFixed(2), +y.toFixed(2), 1]);
      px = x;
      py = y;
    }
    return res;
  });
  myChart.setOption(
    (option = {
      backgroundColor: '#404a59',
      title: {
        text: '微博签到数据点亮中国',
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
        data: ['强', '中', '弱'],
        textStyle: {
          color: '#ccc'
        }
      },
      geo: {
        map: 'china',
        roam: true,
        emphasis: {
          label: {
            show: false
          },
          itemStyle: {
            areaColor: '#2a333d'
          }
        },
        itemStyle: {
          areaColor: '#323c48',
          borderColor: '#111'
        }
      },
      series: [
        {
          name: '弱',
          type: 'scatter',
          coordinateSystem: 'geo',
          symbolSize: 1,
          large: true,
          itemStyle: {
            shadowBlur: 2,
            shadowColor: 'rgba(37, 140, 249, 0.8)',
            color: 'rgba(37, 140, 249, 0.8)'
          },
          data: newWeiboData[0]
        },
        {
          name: '中',
          type: 'scatter',
          coordinateSystem: 'geo',
          symbolSize: 1,
          large: true,
          itemStyle: {
            shadowBlur: 2,
            shadowColor: 'rgba(14, 241, 242, 0.8)',
            color: 'rgba(14, 241, 242, 0.8)'
          },
          data: newWeiboData[1]
        },
        {
          name: '强',
          type: 'scatter',
          coordinateSystem: 'geo',
          symbolSize: 1,
          large: true,
          itemStyle: {
            shadowBlur: 2,
            shadowColor: 'rgba(255, 255, 255, 0.8)',
            color: 'rgba(255, 255, 255, 0.8)'
          },
          data: newWeiboData[2]
        }
      ]
    })
  );
});
```
