# treemap-sunburst-transition

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=treemap-sunburst-transition

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
$.getJSON(
  ROOT_PATH + '/data/asset/data/echarts-package-size.json',
  function (data) {
    const treemapOption = {
      series: [
        {
          type: 'treemap',
          id: 'echarts-package-size',
          animationDurationUpdate: 1000,
          roam: false,
          nodeClick: undefined,
          data: data.children,
          universalTransition: true,
          label: {
            show: true
          },
          breadcrumb: {
            show: false
          }
        }
      ]
    };
    const sunburstOption = {
      series: [
        {
          type: 'sunburst',
          id: 'echarts-package-size',
          radius: ['20%', '90%'],
          animationDurationUpdate: 1000,
          nodeClick: undefined,
          data: data.children,
          universalTransition: true,
          itemStyle: {
            borderWidth: 1,
            borderColor: 'rgba(255,255,255,.5)'
          },
          label: {
            show: false
          }
        }
      ]
    };
    let currentOption = treemapOption;
    myChart.setOption(currentOption);
    setInterval(function () {
      currentOption =
        currentOption === treemapOption ? sunburstOption : treemapOption;
      myChart.setOption(currentOption);
    }, 3000);
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
