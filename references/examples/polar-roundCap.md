# polar-roundCap

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=polar-roundCap

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
option = {
  angleAxis: {
    max: 2,
    startAngle: 30,
    splitLine: {
      show: false
    }
  },
  radiusAxis: {
    type: 'category',
    data: ['v', 'w', 'x', 'y', 'z'],
    z: 10
  },
  polar: {},
  series: [
    {
      type: 'bar',
      data: [4, 3, 2, 1, 0],
      coordinateSystem: 'polar',
      name: 'Without Round Cap',
      itemStyle: {
        borderColor: 'red',
        opacity: 0.8,
        borderWidth: 1
      }
    },
    {
      type: 'bar',
      data: [4, 3, 2, 1, 0],
      coordinateSystem: 'polar',
      name: 'With Round Cap',
      roundCap: true,
      itemStyle: {
        borderColor: 'green',
        opacity: 0.8,
        borderWidth: 1
      }
    }
  ],
  legend: {
    show: true,
    data: ['Without Round Cap', 'With Round Cap']
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
