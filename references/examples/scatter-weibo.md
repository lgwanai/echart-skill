# scatter-weibo

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-weibo

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
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

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `legend: {
        left: 'left',...`

## HTML Shell
```html
<!DOCTYPE html><html lang="zh-CN">
<head><meta charset="utf-8"><title>TITLE</title>
<script>/* ECHARTS_INLINE */</script>
<style>body{margin:0;padding:16px;font-family:sans-serif}#main{width:100%;height:600px}</style>
</head><body><div id="main"></div><script>
var chart = echarts.init(document.getElementById("main"));
// PASTE COMPLETE CODE HERE, replace data arrays with DuckDB real data
chart.setOption(option);
window.addEventListener("resize",function(){chart.resize();});
</script></body></html>
```
