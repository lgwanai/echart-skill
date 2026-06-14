# scatter3D-dataset

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter3D-dataset

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
$.get(
  ROOT_PATH + '/data/asset/data/life-expectancy-table.json',
  function (data) {
    var symbolSize = 2.5;
    option = {
      grid3D: {},
      xAxis3D: {
        type: 'category'
      },
      yAxis3D: {},
      zAxis3D: {},
      dataset: {
        dimensions: [
          'Income',
          'Life Expectancy',
          'Population',
          'Country',
          { name: 'Year', type: 'ordinal' }
        ],
        source: data
      },
      series: [
        {
          type: 'scatter3D',
          symbolSize: symbolSize,
          encode: {
            x: 'Country',
            y: 'Life Expectancy',
            z: 'Income',
            tooltip: [0, 1, 2, 3, 4]
          }
        }
      ]
    };
    myChart.setOption(option);
  }
);
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
