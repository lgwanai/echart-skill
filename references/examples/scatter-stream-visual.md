# scatter-stream-visual

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-stream-visual
**Chart Type:** `cross`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

## Reference Code

```javascript
/*
title: Visual interaction with stream
category: scatter
titleCN: 流式渲染和视觉映射操作
difficulty: 5
*/
// Thanks to: 若怀冰
// http://gallery.echartsjs.com/explore.html?u=bd-16906679
// http://gallery.echartsjs.com/editor.html?c=xHJw-hVqjW
$.getJSON(
  ROOT_PATH + '/data/asset/data/house-price-area2.json',
  function (data) {
    var option = {
      title: {
        text: 'Dispersion of house price based on the area',
        left: 'center',
        top: 0
      },
      visualMap: {
        min: 15202,
        max: 159980,
        dimension: 1,
        orient: 'vertical',
        right: 10,
        top: 'center',
        text: ['HIGH', 'LOW'],
        calculable: true,
        inRange: {
          color: ['#f2c31a', '#24b7f2']
        }
      },
      tooltip: {
        trigger: 'item',
        axisPointer: {
          type: 'cross'
        }
      },
      xAxis: [
        {
          type: 'value'
        }
      ],
      yAxis: [
        {
          type: 'value'
        }
      ],
      series: [
        {
          name: 'price-area',
          type: 'scatter',
          symbolSize: 5,
          data: data
        }
      ]
    };
    myChart.setOption(option);
  }
);
```
