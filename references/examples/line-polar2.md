# line-polar2

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-polar2

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
const data = [];
for (let i = 0; i <= 360; i++) {
  let t = (i / 180) * Math.PI;
  let r = Math.sin(2 * t) * Math.cos(2 * t);
  data.push([r, i]);
}
option = {
  title: {
    text: 'Two Value-Axes in Polar'
  },
  legend: {
    data: ['line']
  },
  polar: {
    center: ['50%', '54%']
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    }
  },
  angleAxis: {
    type: 'value',
    startAngle: 0
  },
  radiusAxis: {
    min: 0
  },
  series: [
    {
      coordinateSystem: 'polar',
      name: 'line',
      type: 'line',
      showSymbol: false,
      data: data
    }
  ],
  animationDuration: 2000
};
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `lue-Axes in Polar'
  },
  legend: {...`

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
