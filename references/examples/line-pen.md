# line-pen

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-pen
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
title: Click to Add Points
category: line
titleCN: 点击添加折线图拐点
difficulty: 9
*/
const symbolSize = 20;
const data = [
  [15, 0],
  [-50, 10],
  [-56.5, 20],
  [-46.5, 30],
  [-22.1, 40]
];
option = {
  title: {
    text: 'Click to Add Points'
  },
  tooltip: {
    formatter: function (params) {
      var data = params.data || [0, 0];
      return data[0].toFixed(2) + ', ' + data[1].toFixed(2);
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    min: -60,
    max: 20,
    type: 'value',
    axisLine: { onZero: false }
  },
  yAxis: {
    min: 0,
    max: 40,
    type: 'value',
    axisLine: { onZero: false }
  },
  series: [
    {
      id: 'a',
      type: 'line',
      smooth: true,
      symbolSize: symbolSize,
      data: data
    }
  ]
};
var zr = myChart.getZr();
zr.on('click', function (params) {
  var pointInPixel = [params.offsetX, params.offsetY];
  var pointInGrid = myChart.convertFromPixel('grid', pointInPixel);
  if (myChart.containPixel('grid', pointInPixel)) {
    data.push(pointInGrid);
    myChart.setOption({
      series: [
        {
          id: 'a',
          data: data
        }
      ]
    });
  }
});
zr.on('mousemove', function (params) {
  var pointInPixel = [params.offsetX, params.offsetY];
  zr.setCursorStyle(
    myChart.containPixel('grid', pointInPixel) ? 'copy' : 'default'
  );
});
```
