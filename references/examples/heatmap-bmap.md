# 热力图与百度地图扩展 / Heatmap on Baidu Map Extension

**Category:** `heatmap`
**Example dir:** `heatmap-bmap`
**Difficulty:** 3

## Template Match
- **calendar/heatmap.html** — Calendar Heatmap

## Option Code
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



## Key Points
- This is an official ECharts example from `heatmap-bmap/main.js`
- Template data format: `[[dateString, value], ...]  (dateString: 'YYYY-MM-DD')`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
