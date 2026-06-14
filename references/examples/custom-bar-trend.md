# custom-bar-trend

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=custom-bar-trend
**Chart Type:** `slider`

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
title: Custom Bar Trend
category: custom
titleCN: 使用自定义系列添加柱状图趋势
difficulty: 3
*/
const yearCount = 7;
const categoryCount = 30;
const xAxisData = [];
const customData = [];
const legendData = [];
const dataList = [];
legendData.push('trend');
const encodeY = [];
for (var i = 0; i < yearCount; i++) {
  legendData.push(2010 + i + '');
  dataList.push([]);
  encodeY.push(1 + i);
}
for (var i = 0; i < categoryCount; i++) {
  var val = Math.random() * 1000;
  xAxisData.push('category' + i);
  var customVal = [i];
  customData.push(customVal);
  for (var j = 0; j < dataList.length; j++) {
    var value =
      j === 0
        ? echarts.number.round(val, 2)
        : echarts.number.round(
            Math.max(0, dataList[j - 1][i] + (Math.random() - 0.5) * 200),
            2
          );
    dataList[j].push(value);
    customVal.push(value);
  }
}
option = {
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: legendData,
    top: 20
  },
  dataZoom: [
    {
      type: 'slider',
      start: 50,
      end: 70
    },
    {
      type: 'inside',
      start: 50,
      end: 70
    }
  ],
  xAxis: {
    data: xAxisData
  },
  yAxis: {},
  series: [
    {
      type: 'custom',
      name: 'trend',
      renderItem: function (params, api) {
        var xValue = api.value(0);
        var currentSeriesIndices = api.currentSeriesIndices();
        var barLayout = api.barLayout({
          barGap: '30%',
          barCategoryGap: '20%',
          count: currentSeriesIndices.length - 1
        });
        var points = [];
        for (var i = 0; i < currentSeriesIndices.length; i++) {
          var seriesIndex = currentSeriesIndices[i];
          if (seriesIndex !== params.seriesIndex) {
            var point = api.coord([xValue, api.value(seriesIndex)]);
            point[0] += barLayout[i - 1].offsetCenter;
            point[1] -= 20;
            points.push(point);
          }
        }
        var style = api.style({
          stroke: api.visual('color'),
          fill: 'none'
        });
        return {
          type: 'polyline',
          shape: {
            points: points
          },
          style: style
        };
      },
      itemStyle: {
        borderWidth: 2
      },
      encode: {
        x: 0,
        y: encodeY
      },
      data: customData,
      z: 100
    },
    ...dataList.map(function (data, index) {
      return {
        type: 'bar',
        animation: false,
        name: legendData[index + 1],
        itemStyle: {
          opacity: 0.5
        },
        data: data
      };
    })
  ]
};
```
