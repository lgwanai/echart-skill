# 日历饼图 / Calendar Pie

**Category:** `'calendar, pie'`
**Example dir:** `calendar-pie`
**Difficulty:** 6

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
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



## Key Points
- This is an official ECharts example from `calendar-pie/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
