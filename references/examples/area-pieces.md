# area-pieces

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=area-pieces

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
option = {
  xAxis: {
    type: 'category',
    boundaryGap: false
  },
  yAxis: {
    type: 'value',
    boundaryGap: [0, '30%']
  },
  visualMap: {
    type: 'piecewise',
    show: false,
    dimension: 0,
    seriesIndex: 0,
    pieces: [
      {
        gt: 1,
        lt: 3,
        color: 'rgba(0, 0, 180, 0.4)'
      },
      {
        gt: 5,
        lt: 7,
        color: 'rgba(0, 0, 180, 0.4)'
      }
    ]
  },
  series: [
    {
      type: 'line',
      smooth: 0.6,
      symbol: 'none',
      lineStyle: {
        color: '#5470C6',
        width: 5
      },
      markLine: {
        symbol: ['none', 'none'],
        label: { show: false },
        data: [{ xAxis: 1 }, { xAxis: 3 }, { xAxis: 5 }, { xAxis: 7 }]
      },
      areaStyle: {},
      data: [
        ['2019-10-10', 200],
        ['2019-10-11', 560],
        ['2019-10-12', 750],
        ['2019-10-13', 580],
        ['2019-10-14', 250],
        ['2019-10-15', 300],
        ['2019-10-16', 450],
        ['2019-10-17', 300],
        ['2019-10-18', 100]
      ]
    }
  ]
};
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `label: { show: false },...`
- `data[1]`: `}]
      },
      areaStyle: {},...`

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
