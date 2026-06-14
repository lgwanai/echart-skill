# custom-ohlc

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=custom-ohlc
**Chart Type:** `group`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **1 data array(s)** to replace:

### data[0]: `legend`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Dow-Jones index']`
- **Replace with**: real data from DuckDB in the same format


## External Data Format

This example uses external data. Format from `stock-DJI.json`:

```json
[
  [
    "2004-01-02",
    10452.74,
    10409.85,
    10367.41,
    10554.96,
    168890000
  ],
  [
    "2004-01-05",
    10411.85,
    10544.07,
    10411.85,
    10575.92,
    221290000
  ],
  [
    "2004-01-06",
    10543.85,
    10538.66,
    10454.37,
    10584.07,
    191460000
  ]
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
title: OHLC Chart
category: candlestick
titleCN: OHLC 图（使用自定义系列）
difficulty: 1
*/
function splitData(rawData) {
  const categoryData = [];
  const values = [];
  for (var i = 0; i < rawData.length; i++) {
    categoryData.push(rawData[i][0]);
    rawData[i][0] = i;
    values.push(rawData[i]);
  }
  return {
    categoryData: categoryData,
    values: values
  };
}
function renderItem(params, api) {
  var xValue = api.value(0);
  var openPoint = api.coord([xValue, api.value(1)]);
  var closePoint = api.coord([xValue, api.value(2)]);
  var lowPoint = api.coord([xValue, api.value(3)]);
  var highPoint = api.coord([xValue, api.value(4)]);
  var halfWidth = api.size([1, 0])[0] * 0.35;
  var style = api.style({
    stroke: api.visual('color')
  });
  return {
    type: 'group',
    children: [
      {
        type: 'line',
        shape: {
          x1: lowPoint[0],
          y1: lowPoint[1],
          x2: highPoint[0],
          y2: highPoint[1]
        },
        style: style
      },
      {
        type: 'line',
        shape: {
          x1: openPoint[0],
          y1: openPoint[1],
          x2: openPoint[0] - halfWidth,
          y2: openPoint[1]
        },
        style: style
      },
      {
        type: 'line',
        shape: {
          x1: closePoint[0],
          y1: closePoint[1],
          x2: closePoint[0] + halfWidth,
          y2: closePoint[1]
        },
        style: style
      }
    ]
  };
}
$.get(ROOT_PATH + '/data/asset/data/stock-DJI.json', function (rawData) {
  var data = splitData(rawData);
  myChart.setOption(
    (option = {
      animation: false,
      legend: {
        bottom: 10,
        left: 'center',
        data: ['Dow-Jones index']
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        position: function (pos, params, el, elRect, size) {
          var obj = { top: 10 };
          obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
          return obj;
        }
      },
      axisPointer: {
        link: [{ xAxisIndex: 'all' }]
      },
      toolbox: {
        feature: {
          dataZoom: {
            yAxisIndex: false
          },
          brush: {
            type: ['lineX', 'clear']
          }
        }
      },
      grid: [
        {
          left: '10%',
          right: '8%',
          bottom: 150
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: data.categoryData,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          min: 'dataMin',
          max: 'dataMax',
          axisPointer: {
            z: 100
          }
        }
      ],
      yAxis: [
        {
          scale: true,
          splitArea: {
            show: true
          }
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          start: 98,
          end: 100,
          minValueSpan: 10
        },
        {
          show: true,
          type: 'slider',
          bottom: 60,
          start: 98,
          end: 100,
          minValueSpan: 10
        }
      ],
      series: [
        {
          name: 'Dow-Jones index',
          type: 'custom',
          renderItem: renderItem,
          dimensions: ['-', 'open', 'close', 'lowest', 'highest'],
          encode: {
            x: 0,
            y: [1, 2, 3, 4],
            tooltip: [1, 2, 3, 4]
          },
          data: data.values
        }
      ]
    }),
    true
  );
});
```
