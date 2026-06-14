# globe-country-carousel

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=globe-country-carousel

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
var canvas = document.createElement('canvas');
var mapChart = echarts.init(canvas, null, {
  width: 2048,
  height: 1024
});
mapChart.setOption({
  backgroundColor: '#999',
  geo: {
    type: 'map',
    map: 'world',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    boundingCoords: [
      [-180, 90],
      [180, -90]
    ],
    silent: true,
    itemStyle: {
      borderColor: '#000'
    },
    label: {
      color: '#fff',
      fontSize: 40
    }
  }
});
option = {
  globe: {
    baseTexture: mapChart,
    heightTexture: ROOT_PATH + '/data-gl/asset/bathymetry_bw_composite_4k.jpg',
    displacementScale: 0.1,
    shading: 'realistic',
    realisticMaterial: {
      roughness: 0.8,
      metalness: 0
    },
    postEffect: {
      enable: true
    },
    temporalSuperSampling: {
      enable: true
    },
    light: {
      ambient: {
        intensity: 0
      },
      main: {
        intensity: 2,
        shadow: true
      },
      ambientCubemap: {
        texture: ROOT_PATH + '/data-gl/asset/lake.hdr',
        exposure: 1,
        diffuseIntensity: 0.2
      }
    },
    viewControl: {
      animationDurationUpdate: 1000,
      animationEasingUpdate: 'cubicInOut',
      targetCoord: [116.46, 39.92],
      autoRotate: false
    }
  },
  series: []
};
var regions = mapChart.getModel().getComponent('geo').coordinateSystem.regions;
setInterval(function () {
  var region = regions[Math.round(Math.random() * (regions.length - 1))];
  myChart.setOption({
    title: {
      left: 'center',
      top: 'center',
      text: region.name,
      textStyle: {
        fontSize: 40
      }
    },
    globe: {
      viewControl: {
        targetCoord: region.center
      }
    }
  });
  mapChart.setOption({
    geo: {
      regions: [
        {
          name: region.name,
          itemStyle: {
            normal: {
              areaColor: '#444'
            }
          }
        }
      ]
    }
  });
}, 2000);
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
