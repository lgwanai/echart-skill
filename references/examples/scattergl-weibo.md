# scattergl-weibo

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scattergl-weibo

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
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
