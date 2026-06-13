# 横向日历图 / Calendar Heatmap Horizontal

**Category:** `calendar`
**Example dir:** `calendar-horizontal`
**Difficulty:** 2

## Template Match
- **calendar/heatmap.html** — Calendar Heatmap

## Option Code
```javascript
function getVirtualData(year) {
  const date = +echarts.time.parse(year + '-01-01');
  const end = +echarts.time.parse(+year + 1 + '-01-01');
  const dayTime = 3600 * 24 * 1000;
  const data = [];
  for (let time = date; time < end; time += dayTime) {
    data.push([
      echarts.time.format(time, '{yyyy}-{MM}-{dd}', false),
      Math.floor(Math.random() * 1000)
    ]);
  }
  return data;
}
option = {
  tooltip: {
    position: 'top'
  },
  visualMap: {
    min: 0,
    max: 1000,
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    top: 'top'
  },
  calendar: [
    {
      range: '2017',
      cellSize: ['auto', 20]
    },
    {
      top: 260,
      range: '2016',
      cellSize: ['auto', 20]
    },
    {
      top: 450,
      range: '2015',
      cellSize: ['auto', 20],
      right: 5
    }
  ],
  series: [
    {
      type: 'heatmap',
      coordinateSystem: 'calendar',
      calendarIndex: 0,
      data: getVirtualData('2017')
    },
    {
      type: 'heatmap',
      coordinateSystem: 'calendar',
      calendarIndex: 1,
      data: getVirtualData('2016')
    },
    {
      type: 'heatmap',
      coordinateSystem: 'calendar',
      calendarIndex: 2,
      data: getVirtualData('2015')
    }
  ]
};
```



## Key Points
- This is an official ECharts example from `calendar-horizontal/main.js`
- Template data format: `[[dateString, value], ...]  (dateString: 'YYYY-MM-DD')`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
