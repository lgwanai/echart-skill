# heatmap-bmap

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=heatmap-bmap

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
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
