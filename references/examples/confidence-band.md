# confidence-band

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=confidence-band
**Chart Type:** `cross`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `confidence-band.json`:

```json
[
  {
    "value": -1.1618426259,
    "date": "2012-08-28",
    "l": -2.6017329022,
    "u": 0.2949717757
  },
  {
    "value": -0.5828247293,
    "date": "2012-08-29",
    "l": -1.3166963635,
    "u": 0.1324086347
  },
  {
    "value": -0.3790770636,
    "date": "2012-08-30",
    "l": -0.8712221305,
    "u": 0.0956413566
  }
]
```

Agent: build DuckDB query to produce matching data structure.
## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

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
