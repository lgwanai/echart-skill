# globe-atmosphere

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=globe-atmosphere

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
option = {
  backgroundColor: '#000',
  globe: {
    baseTexture: ROOT_PATH + '/data-gl/asset/earth.jpg',
    shading: 'lambert',
    environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
    atmosphere: {
      show: true
    },
    light: {
      ambient: {
        intensity: 0.1
      },
      main: {
        intensity: 1.5
      }
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
