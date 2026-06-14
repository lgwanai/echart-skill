# geo3d-with-different-height

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=geo3d-with-different-height

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
$.getJSON(
  ROOT_PATH + '/data-gl/asset/data/world-population.json',
  function (populationData) {
    var max = -Infinity;
    var min = Infinity;
    populationData.forEach(function (item) {
      max = Math.max(Math.log(item.value), max);
      min = Math.min(Math.log(item.value), min);
    });
    var regions = populationData.map(function (item) {
      return {
        name: item.name,
        height: ((Math.log(item.value) - min) / (max - min)) * 3
      };
    });
    myChart.setOption(
      (option = {
        backgroundColor: '#cdcfd5',
        geo3D: {
          map: 'world',
          shading: 'lambert',
          lambertMaterial: {
            detailTexture: ROOT_PATH + '/data-gl/asset/woods.jpg',
            textureTiling: 20
          },
          postEffect: {
            enable: true,
            SSAO: {
              enable: true,
              radius: 3,
              quality: 'high'
            }
          },
          groundPlane: {
            show: true
          },
          light: {
            main: {
              intensity: 1,
              shadow: true,
              shadowQuality: 'high',
              alpha: 30
            },
            ambient: {
              intensity: 0
            },
            ambientCubemap: {
              texture: ROOT_PATH + '/data-gl/asset/canyon.hdr',
              exposure: 2,
              diffuseIntensity: 0.3
            }
          },
          viewControl: {
            distance: 50
          },
          regionHeight: 0.5,
          regions: regions
        }
      })
    );
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
