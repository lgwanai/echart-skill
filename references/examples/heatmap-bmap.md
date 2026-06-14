# 热力图与百度地图扩展

**Category:** `heatmap`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=heatmap-bmap
**Template:** heatmap/basic.html
**Data Format:** `{ xLabels: string[], yLabels: string[], data: [[xIdx, yIdx, value], ...] }`
**Features:** visualMap component required

## Official Option Code

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

## Placeholders

| Placeholder | Type | Description |
|-------------|------|-------------|
| `{{{TITLE}}}` | string | title |

## Usage
- Build: `scripts/build_template.py heatmap/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
