# scatter3d-scatter

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter3d-scatter

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: 3D Scatter with Scatter Matrix
category: scatter3D
titleCN: ä¸ç»´æ£ç¹å¾åæ£ç¹ç©éµç»åä½¿ç¨
*/
$.get(
  ROOT_PATH + '/data/asset/data/life-expectancy-table.json',
  function (data) {
    var sizeValue = '57%';
    var symbolSize = 2.5;
    option = {
      tooltip: {},
      grid3D: {
        width: '50%'
      },
      xAxis3D: {},
      yAxis3D: {},
      zAxis3D: {},
      grid: [
        { left: '50%', width: '20%', bottom: sizeValue },
        { left: '75%', width: '20%', bottom: sizeValue },
        { left: '50%', width: '20%', top: sizeValue },
        { left: '75%', width: '20%', top: sizeValue }
      ],
      xAxis: [
        {
          type: 'value',
          gridIndex: 0,
          name: 'Income',
          axisLabel: { rotate: 50, interval: 0 }
        },
        {
          type: 'category',
          gridIndex: 1,
          name: 'Country',
          boundaryGap: false,
          axisLabel: { rotate: 50, interval: 0 }
        },
        {
          type: 'value',
          gridIndex: 2,
          name: 'Income',
          axisLabel: { rotate: 50, interval: 0 }
        },
        {
          type: 'value',
          gridIndex: 3,
          name: 'Life Expectancy',
          axisLabel: { rotate: 50, interval: 0 }
        }
      ],
      yAxis: [
        { type: 'value', gridIndex: 0, name: 'Life Expectancy' },
        { type: 'value', gridIndex: 1, name: 'Income' },
        { type: 'value', gridIndex: 2, name: 'Population' },
        { type: 'value', gridIndex: 3, name: 'Population' }
      ],
      dataset: {
        dimensions: [
          'Income',
          'Life Expectancy',
          'Population',
          'Country',
          { name: 'Year', type: 'ordinal' }
        ],
        source: data
      },
      series: [
        {
          type: 'scatter3D',
          symbolSize: 3,
          encode: {
            x: 'Population',
            y: 'Life Expectancy',
            z: 'Income',
            tooltip: [0, 1, 2, 3, 4]
          }
        },
        {
          type: 'scatter',
          symbolSize: symbolSize,
          xAxisIndex: 0,
          yAxisIndex: 0,
          encode: {
            x: 'Income',
            y: 'Life Expectancy',
            tooltip: [0, 1, 2, 3, 4]
          }
        },
        {
          type: 'scatter',
          symbolSize: symbolSize,
          xAxisIndex: 1,
          yAxisIndex: 1,
          encode: {
            x: 'Country',
            y: 'Income',
            tooltip: [0, 1, 2, 3, 4]
          }
        },
        {
          type: 'scatter',
          symbolSize: symbolSize,
          xAxisIndex: 2,
          yAxisIndex: 2,
          encode: {
            x: 'Income',
            y: 'Population',
            tooltip: [0, 1, 2, 3, 4]
          }
        },
        {
          type: 'scatter',
          symbolSize: symbolSize,
          xAxisIndex: 3,
          yAxisIndex: 3,
          encode: {
            x: 'Life Expectancy',
            y: 'Population',
            tooltip: [0, 1, 2, 3, 4]
          }
        }
      ]
    };
    myChart.setOption(option);
  }
);
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
