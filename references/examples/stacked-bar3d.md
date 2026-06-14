# stacked-bar3d

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=stacked-bar3d

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
$.getScript(CDN_PATH + 'simplex-noise@2.4.0/simplex-noise.js').done(
  function () {
    function generateData() {
      var data = [];
      var noise = new SimplexNoise(Math.random);
      for (var i = 0; i <= 10; i++) {
        for (var j = 0; j <= 10; j++) {
          var value = noise.noise2D(i / 5, j / 5);
          data.push([i, j, value * 2 + 4]);
        }
      }
      return data;
    }
    var series = [];
    for (var i = 0; i < 10; i++) {
      series.push({
        type: 'bar3D',
        data: generateData(),
        stack: 'stack',
        shading: 'lambert',
        emphasis: {
          label: {
            show: false
          }
        }
      });
    }
    myChart.setOption({
      xAxis3D: {
        type: 'value'
      },
      yAxis3D: {
        type: 'value'
      },
      zAxis3D: {
        type: 'value'
      },
      grid3D: {
        viewControl: {
          // autoRotate: true
        },
        light: {
          main: {
            shadow: true,
            quality: 'ultra',
            intensity: 1.5
          }
        }
      },
      series: series
    });
  }
);
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
