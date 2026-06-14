# mix-zoom-on-value

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=mix-zoom-on-value

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
myChart.showLoading();
$.get(
  ROOT_PATH + '/data/asset/data/obama_budget_proposal_2012.list.json',
  function (obama_budget_2012) {
    myChart.hideLoading();
    option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
          label: {
            show: true
          }
        }
      },
      toolbox: {
        show: true,
        feature: {
          mark: { show: true },
          dataView: { show: true, readOnly: false },
          magicType: { show: true, type: ['line', 'bar'] },
          restore: { show: true },
          saveAsImage: { show: true }
        }
      },
      calculable: true,
      legend: {
        data: ['Growth', 'Budget 2011', 'Budget 2012'],
        itemGap: 5
      },
      grid: {
        top: '12%',
        left: '1%',
        right: '10%',
        containLabel: true
      },
      xAxis: [
        {
          type: 'category',
          data: obama_budget_2012.names
        }
      ],
      yAxis: [
        {
          type: 'value',
          name: 'Budget (million USD)',
          axisLabel: {
            formatter: function (a) {
              a = +a;
              return isFinite(a) ? echarts.format.addCommas(+a / 1000) : '';
            }
          }
        }
      ],
      dataZoom: [
        {
          show: true,
          start: 94,
          end: 100
        },
        {
          type: 'inside',
          start: 94,
          end: 100
        },
        {
          show: true,
          yAxisIndex: 0,
          filterMode: 'empty',
          width: 30,
          height: '80%',
          showDataShadow: false,
          left: '93%'
        }
      ],
      series: [
        {
          name: 'Budget 2011',
          type: 'bar',
          data: obama_budget_2012.budget2011List
        },
        {
          name: 'Budget 2012',
          type: 'bar',
          data: obama_budget_2012.budget2012List
        }
      ]
    };
    myChart.setOption(option);
  }
);
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `lculable: true,
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
