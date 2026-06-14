# funnel-align

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=funnel-align

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
option = {
  title: {
    text: 'Funnel Compare',
    subtext: 'Fake Data',
    left: 'left',
    top: 'bottom'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b} : {c}%'
  },
  toolbox: {
    show: true,
    orient: 'vertical',
    top: 'center',
    feature: {
      dataView: { readOnly: false },
      restore: {},
      saveAsImage: {}
    }
  },
  legend: {
    orient: 'vertical',
    left: 'left',
    data: ['Prod A', 'Prod B', 'Prod C', 'Prod D', 'Prod E']
  },
  series: [
    {
      name: 'Funnel',
      type: 'funnel',
      width: '40%',
      height: '45%',
      left: '5%',
      top: '50%',
      funnelAlign: 'right',
      data: [
        { value: 60, name: 'Prod C' },
        { value: 30, name: 'Prod D' },
        { value: 10, name: 'Prod E' },
        { value: 80, name: 'Prod B' },
        { value: 100, name: 'Prod A' }
      ]
    },
    {
      name: 'Pyramid',
      type: 'funnel',
      width: '40%',
      height: '45%',
      left: '5%',
      top: '5%',
      sort: 'ascending',
      funnelAlign: 'right',
      data: [
        { value: 60, name: 'Prod C' },
        { value: 30, name: 'Prod D' },
        { value: 10, name: 'Prod E' },
        { value: 80, name: 'Prod B' },
        { value: 100, name: 'Prod A' }
      ]
    },
    {
      name: 'Funnel',
      type: 'funnel',
      width: '40%',
      height: '45%',
      left: '55%',
      top: '5%',
      funnelAlign: 'left',
      data: [
        { value: 60, name: 'Prod C' },
        { value: 30, name: 'Prod D' },
        { value: 10, name: 'Prod E' },
        { value: 80, name: 'Prod B' },
        { value: 100, name: 'Prod A' }
      ]
    },
    {
      name: 'Pyramid',
      type: 'funnel',
      width: '40%',
      height: '45%',
      left: '55%',
      top: '50%',
      sort: 'ascending',
      funnelAlign: 'left',
      data: [
        { value: 60, name: 'Prod C' },
        { value: 30, name: 'Prod D' },
        { value: 10, name: 'Prod E' },
        { value: 80, name: 'Prod B' },
        { value: 100, name: 'Prod A' }
      ]
    }
  ]
};
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `ient: 'vertical',
    left: 'left',...`
- `data[1]`: `50%',
      funnelAlign: 'right',...`
- `data[2]`: `ing',
      funnelAlign: 'right',...`
- `data[3]`: `'5%',
      funnelAlign: 'left',...`
- `data[4]`: `ding',
      funnelAlign: 'left',...`

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
