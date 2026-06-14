# globe-echarts-gl-hello-world

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=globe-echarts-gl-hello-world

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
option = {
  backgroundColor: '#000',
  globe: {
    baseTexture: ROOT_PATH + '/data-gl/asset/world.topo.bathy.200401.jpg',
    heightTexture: ROOT_PATH + '/data-gl/asset/world.topo.bathy.200401.jpg',
    displacementScale: 0.04,
    shading: 'realistic',
    environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
    realisticMaterial: {
      roughness: 0.9
    },
    postEffect: {
      enable: true
    },
    light: {
      main: {
        intensity: 5,
        shadow: true
      },
      ambientCubemap: {
        texture: ROOT_PATH + '/data-gl/asset/pisa.hdr',
        diffuseIntensity: 0.2
      }
    }
  }
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
