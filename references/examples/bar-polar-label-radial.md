# bar-polar-label-radial

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-polar-label-radial

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
option = {
  title: [
    {
      text: 'Radial Polar Bar Label Position (middle)'
    }
  ],
  polar: {
    radius: [30, '80%']
  },
  radiusAxis: {
    max: 4
  },
  angleAxis: {
    type: 'category',
    data: ['a', 'b', 'c', 'd'],
    startAngle: 75
  },
  tooltip: {},
  series: {
    type: 'bar',
    data: [2, 1.2, 2.4, 3.6],
    coordinateSystem: 'polar',
    label: {
      show: true,
      position: 'middle',
      formatter: '{b}: {c}'
    }
  },
  animation: false
};
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `angleAxis: {
    type: 'category',...`
- `data[1]`: `p: {},
  series: {
    type: 'bar',...`

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
