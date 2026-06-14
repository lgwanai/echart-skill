# lines3d-flights-on-geo3d

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=lines3d-flights-on-geo3d

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
$.getJSON(ROOT_PATH + '/data-gl/asset/data/flights.json', function (data) {
  function getAirportCoord(idx) {
    return [data.airports[idx][3], data.airports[idx][4]];
  }
  var routes = data.routes.map(function (airline) {
    return [getAirportCoord(airline[1]), getAirportCoord(airline[2])];
  });
  myChart.setOption({
    geo3D: {
      map: 'world',
      shading: 'color',
      environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
      silent: true,
      groundPlane: {
        show: false
      },
      light: {
        main: {
          intensity: 0
        },
        ambient: {
          intensity: 0
        }
      },
      viewControl: {
        distance: 50
      },
      itemStyle: {
        color: '#111'
      },
      boxHeight: 0.5
    },
    series: [
      {
        type: 'lines3D',
        coordinateSystem: 'geo3D',
        effect: {
          show: true,
          trailWidth: 2,
          trailLength: 0.2
        },
        blendMode: 'lighter',
        lineStyle: {
          width: 0,
          color: 'rgb(50, 50, 150)',
          opacity: 0.2
        },
        data: routes
      }
    ]
  });
});
window.addEventListener('keydown', function () {
  myChart.dispatchAction({
    type: 'lines3DToggleEffect',
    seriesIndex: 0
  });
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
