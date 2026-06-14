# map3d-alcohol-consumption

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=map3d-alcohol-consumption

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
$.getJSON(ROOT_PATH + '/data-gl/asset/data/alcohol.json', function (data) {
  var regionData = data.map(function (item) {
    return {
      name: item[0],
      value: item[1]
    };
  });
  console.log(regionData);
  myChart.setOption({
    backgroundColor: '#cdcfd5',
    visualMap: {
      min: 0,
      max: 15,
      realtime: true,
      calculable: true,
      inRange: {
        color: [
          '#313695',
          '#4575b4',
          '#74add1',
          '#abd9e9',
          '#e0f3f8',
          '#ffffbf',
          '#fee090',
          '#fdae61',
          '#f46d43',
          '#d73027',
          '#a50026'
        ]
      }
    },
    series: [
      {
        type: 'map3D',
        map: 'world',
        shading: 'lambert',
        realisticMaterial: {
          roughness: 0.2,
          metalness: 0
        },
        postEffect: {
          enable: true,
          SSAO: {
            enable: true,
            radius: 2,
            intensity: 1
          }
        },
        groundPlane: {
          show: true
        },
        light: {
          main: {
            intensity: 2,
            shadow: true,
            shadowQuality: 'high',
            alpha: 30
          },
          ambient: {
            intensity: 0
          },
          ambientCubemap: {
            texture: ROOT_PATH + '/data-gl/asset/canyon.hdr',
            exposure: 1,
            diffuseIntensity: 1
          }
        },
        viewControl: {
          distance: 50
        },
        regionHeight: 1,
        data: regionData
      }
    ]
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
