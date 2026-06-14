# scatter-weibo

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-weibo
**Chart Type:** `scatter`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: need **x** + **y** columns (both numeric)
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

Data arrays to replace: **1**

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
