# parallel-simple

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=parallel-simple

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
option = {
  parallelAxis: [
    { dim: 0, name: 'Price' },
    { dim: 1, name: 'Net Weight' },
    { dim: 2, name: 'Amount' },
    {
      dim: 3,
      name: 'Score',
      type: 'category',
      data: ['Excellent', 'Good', 'OK', 'Bad']
    }
  ],
  series: {
    type: 'parallel',
    lineStyle: {
      width: 4
    },
    data: [
      [12.99, 100, 82, 'Good'],
      [9.99, 80, 77, 'OK'],
      [20, 120, 60, 'Excellent']
    ]
  }
};
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `'Score',
      type: 'category',...`
- `data[1]`: `lineStyle: {
      width: 4
    },...`

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
