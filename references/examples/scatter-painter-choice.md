# scatter-painter-choice

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-painter-choice

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
myChart.showLoading();
$.get(
  ROOT_PATH + '/data/asset/data/masterPainterColorChoice.json',
  function (json) {
    myChart.hideLoading();
    var data = json[0].x.map(function (x, idx) {
      return [+x, +json[0].y[idx]];
    });
    myChart.setOption(
      (option = {
        title: {
          text: 'Master Painter Color Choices Throughout History',
          subtext: 'Data From Plot.ly',
          left: 'right'
        },
        xAxis: {
          type: 'value',
          splitLine: {
            show: false
          },
          scale: true,
          splitNumber: 5,
          max: 'dataMax',
          axisLabel: {
            formatter: function (val) {
              return val + 's';
            }
          }
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 360,
          interval: 60,
          name: 'Hue',
          splitLine: {
            show: false
          }
        },
        series: [
          {
            name: 'scatter',
            type: 'scatter',
            symbolSize: function (val, param) {
              return (
                json[0].marker.size[param.dataIndex] / json[0].marker.sizeref
              );
            },
            itemStyle: {
              color: function (param) {
                return json[0].marker.color[param.dataIndex];
              }
            },
            data: data
          }
        ]
      })
    );
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
