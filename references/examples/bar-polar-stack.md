# bar-polar-stack

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-polar-stack

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
option = {
  angleAxis: {},
  radiusAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu'],
    z: 10
  },
  polar: {},
  series: [
    {
      type: 'bar',
      data: [1, 2, 3, 4],
      coordinateSystem: 'polar',
      name: 'A',
      stack: 'a',
      emphasis: {
        focus: 'series'
      }
    },
    {
      type: 'bar',
      data: [2, 4, 6, 8],
      coordinateSystem: 'polar',
      name: 'B',
      stack: 'a',
      emphasis: {
        focus: 'series'
      }
    },
    {
      type: 'bar',
      data: [1, 2, 3, 4],
      coordinateSystem: 'polar',
      name: 'C',
      stack: 'a',
      emphasis: {
        focus: 'series'
      }
    }
  ],
  legend: {
    show: true,
    data: ['A', 'B', 'C']
  }
};
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `radiusAxis: {
    type: 'category',...`
- `data[1]`: `eries: [
    {
      type: 'bar',...`
- `data[2]`: `}
    },
    {
      type: 'bar',...`
- `data[3]`: `}
    },
    {
      type: 'bar',...`
- `data[4]`: `}
  ],
  legend: {
    show: true,...`

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
