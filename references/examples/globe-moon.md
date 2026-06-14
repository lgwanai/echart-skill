# globe-moon

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=globe-moon

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
option = {
  globe: {
    baseTexture: ROOT_PATH + '/data-gl/asset/moon-base.jpg',
    heightTexture: ROOT_PATH + '/data-gl/asset/moon-bump.jpg',
    displacementScale: 0.05,
    displacementQuality: 'medium',
    environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
    shading: 'realistic',
    realisticMaterial: {
      roughness: 0.8,
      metalness: 0
    },
    postEffect: {
      enable: true,
      SSAO: {
        enable: true,
        radius: 2,
        intensity: 1,
        quality: 'high'
      }
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
        texture: ROOT_PATH + '/data-gl/asset/pisa.hdr',
        exposure: 0,
        diffuseIntensity: 0.02
      }
    },
    viewControl: {
      autoRotate: false
    }
  },
  series: []
};
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
