# calendar-pie

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=calendar-pie

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

**2 data arrays** to replace:
- `data[0]`: `data: [
      { name: 'Work', value: Math.round(Math.random() * 24) },
      { n...`
- `data[1]`: `data: ['Work', 'Entertainment', 'Sleep']`

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Calendar Pie
category: 'calendar, pie'
titleCN: 日历饼图
difficulty: 6
*/
// This example requires ECharts v5.4.0 or later
const cellSize = [80, 80];
const pieRadius = 30;
function getVirtualData() {
  const date = +echarts.time.parse('2017-02-01');
  const end = +echarts.time.parse('2017-03-01');
  const dayTime = 3600 * 24 * 1000;
  const data = [];
  for (let time = date; time < end; time += dayTime) {
    data.push([
      echarts.time.format(time, '{yyyy}-{MM}-{dd}', false),
      Math.floor(Math.random() * 10000)
    ]);
  }
  return data;
}
const scatterData = getVirtualData();
const pieSeries = scatterData.map(function (item, index) {
  return {
    type: 'pie',
    id: 'pie-' + index,
    center: item[0],
    radius: pieRadius,
    coordinateSystem: 'calendar',
    label: {
      formatter: '{c}',
      position: 'inside'
    },
    data: [
      { name: 'Work', value: Math.round(Math.random() * 24) },
      { name: 'Entertainment', value: Math.round(Math.random() * 24) },
      { name: 'Sleep', value: Math.round(Math.random() * 24) }
    ]
  };
});
option = {
  tooltip: {},
  legend: {
    data: ['Work', 'Entertainment', 'Sleep'],
    bottom: 20
  },
  calendar: {
    top: 'middle',
    left: 'center',
    orient: 'vertical',
    cellSize: cellSize,
    yearLabel: {
      show: false,
      fontSize: 30
    },
    dayLabel: {
      margin: 20,
      firstDay: 1,
      nameMap: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    },
    monthLabel: {
      show: false
    },
    range: ['2017-02']
  },
  series: [
    {
      id: 'label',
      type: 'scatter',
      coordinateSystem: 'calendar',
      symbolSize: 0,
      label: {
        show: true,
        formatter: function (params) {
          return echarts.time.format(params.value[0], '{dd}', false);
        },
        offset: [-cellSize[0] / 2 + 10, -cellSize[1] / 2 + 10],
        fontSize: 14
      },
      data: scatterData
    },
    ...pieSeries
  ]
};
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
