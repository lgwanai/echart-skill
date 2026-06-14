# scatter-large

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-large

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
function genData(len, offset) {
  let arr = new Float32Array(len * 2);
  let off = 0;
  for (let i = 0; i < len; i++) {
    let x = +Math.random() * 10;
    let y =
      +Math.sin(x) -
      x * (len % 2 ? 0.1 : -0.1) * Math.random() +
      (offset || 0) / 10;
    arr[off++] = x;
    arr[off++] = y;
  }
  return arr;
}
const data1 = genData(5e5);
const data2 = genData(5e5, 10);
option = {
  title: {
    text:
      echarts.format.addCommas(data1.length / 2 + data2.length / 2) + ' Points'
  },
  tooltip: {},
  toolbox: {
    left: 'center',
    feature: {
      dataZoom: {}
    }
  },
  legend: {
    orient: 'vertical',
    right: 10
  },
  xAxis: [{}],
  yAxis: [{}],
  dataZoom: [
    {
      type: 'inside'
    },
    {
      type: 'slider'
    }
  ],
  animation: false,
  series: [
    {
      name: 'A',
      type: 'scatter',
      data: data1,
      dimensions: ['x', 'y'],
      symbolSize: 3,
      itemStyle: {
        opacity: 0.4
      },
      large: true
    },
    {
      name: 'B',
      type: 'scatter',
      data: data2,
      dimensions: ['x', 'y'],
      symbolSize: 3,
      itemStyle: {
        opacity: 0.4
      },
      large: true
    }
  ]
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
