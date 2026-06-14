# scatter-painter-choice

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-painter-choice
**Chart Type:** `value`

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
title: Master Painter Color Choices Throughout History
category: scatter
titleCN: 历代绘画大师的色彩运用
difficulty: 9
*/
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
