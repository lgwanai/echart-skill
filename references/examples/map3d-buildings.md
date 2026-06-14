# map3d-buildings

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=map3d-buildings

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
$.getJSON(
  ROOT_PATH + '/data-gl/asset/data/buildings.json',
  function (buildingsGeoJSON) {
    echarts.registerMap('buildings', buildingsGeoJSON);
    var regions = buildingsGeoJSON.features.map(function (feature) {
      return {
        name: feature.properties.name,
        value: Math.random(),
        height: feature.properties.height / 10
      };
    });
    myChart.setOption({
      visualMap: {
        show: false,
        min: 0.4,
        max: 1,
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
          map: 'buildings',
          shading: 'realistic',
          environment: '#000',
          realisticMaterial: {
            roughness: 0.6,
            textureTiling: 20
          },
          postEffect: {
            enable: true,
            SSAO: {
              enable: true,
              intensity: 1.3,
              radius: 5
            },
            screenSpaceReflection: {
              enable: false
            },
            depthOfField: {
              enable: true,
              blurRadius: 4,
              focalDistance: 30
            }
          },
          light: {
            main: {
              intensity: 3,
              alpha: 40,
              shadow: true,
              shadowQuality: 'high'
            },
            ambient: {
              intensity: 0
            },
            ambientCubemap: {
              texture: ROOT_PATH + '/data-gl/asset/pisa.hdr',
              exposure: 1,
              diffuseIntensity: 0.5,
              specularIntensity: 1
            }
          },
          groundPlane: {
            show: false,
            color: '#333'
          },
          viewControl: {
            minBeta: -360,
            maxBeta: 360,
            alpha: 50,
            center: [50, 0, -10],
            distance: 30,
            minDistance: 5,
            panMouseButton: 'left',
            rotateMouseButton: 'middle',
            zoomSensitivity: 0.5
          },
          itemStyle: {
            areaColor: '#666'
            // borderColor: '#222',
            // borderWidth: 1
          },
          label: {
            color: 'white'
          },
          silent: true,
          instancing: true,
          boxWidth: 200,
          boxHeight: 1,
          data: regions
        }
      ]
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
