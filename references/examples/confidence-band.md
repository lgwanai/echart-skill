# confidence-band

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=confidence-band
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
title: Confidence Band
category: line
titleCN: 置信带
difficulty: 4
*/
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/data/confidence-band.json', function (data) {
  myChart.hideLoading();
  var base = -data.reduce(function (min, val) {
    return Math.floor(Math.min(min, val.l));
  }, Infinity);
  myChart.setOption(
    (option = {
      title: {
        text: 'Confidence Band',
        subtext: 'Example in MetricsGraphics.js',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          animation: false,
          label: {
            backgroundColor: '#ccc',
            borderColor: '#aaa',
            borderWidth: 1,
            shadowBlur: 0,
            shadowOffsetX: 0,
            shadowOffsetY: 0,
            color: '#222'
          }
        },
        formatter: function (params) {
          return (
            params[2].name +
            '<br />' +
            ((params[2].value - base) * 100).toFixed(1) +
            '%'
          );
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: data.map(function (item) {
          return item.date;
        }),
        axisLabel: {
          formatter: function (value, idx) {
            var date = new Date(value);
            return idx === 0
              ? value
              : [date.getMonth() + 1, date.getDate()].join('-');
          }
        },
        boundaryGap: false
      },
      yAxis: {
        axisLabel: {
          formatter: function (val) {
            return (val - base) * 100 + '%';
          }
        },
        axisPointer: {
          label: {
            formatter: function (params) {
              return ((params.value - base) * 100).toFixed(1) + '%';
            }
          }
        },
        splitNumber: 3
      },
      series: [
        {
          name: 'L',
          type: 'line',
          data: data.map(function (item) {
            return item.l + base;
          }),
          lineStyle: {
            opacity: 0
          },
          stack: 'confidence-band',
          symbol: 'none'
        },
        {
          name: 'U',
          type: 'line',
          data: data.map(function (item) {
            return item.u - item.l;
          }),
          lineStyle: {
            opacity: 0
          },
          areaStyle: {
            color: '#ccc'
          },
          stack: 'confidence-band',
          symbol: 'none'
        },
        {
          type: 'line',
          data: data.map(function (item) {
            return item.value + base;
          }),
          itemStyle: {
            color: '#333'
          },
          showSymbol: false
        }
      ]
    })
  );
});
```
