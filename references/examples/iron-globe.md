# iron-globe

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=iron-globe

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
option = {
  backgroundColor: '#000',
  globe: {
    baseTexture: ROOT_PATH + '/data-gl/asset/world.topo.bathy.200401.jpg',
    heightTexture: ROOT_PATH + '/data-gl/asset/bathymetry_bw_composite_4k.jpg',
    displacementScale: 0.2,
    shading: 'realistic',
    environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
    realisticMaterial: {
      roughness: ROOT_PATH + '/asset/get/s/data-1497599804873-H1SHkG-mZ.jpg',
      metalness: ROOT_PATH + '/asset/get/s/data-1497599800643-BJbHyGWQW.jpg',
      textureTiling: [8, 4]
    },
    postEffect: {
      enable: true
    },
    viewControl: {
      autoRotate: false
    },
    light: {
      main: {
        intensity: 2,
        shadow: true
      },
      ambientCubemap: {
        texture: ROOT_PATH + '/data-gl/asset/pisa.hdr',
        exposure: 2,
        diffuseIntensity: 2,
        specularIntensity: 2
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
