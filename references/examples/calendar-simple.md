# 基础日历图 / Simple Calendar

**Category:** `calendar`
**Example dir:** `calendar-simple`
**Difficulty:** 0

## Template Match
- **calendar/heatmap.html** — Calendar Heatmap

## Option Code
```javascript
function getVirtualData(year) {
  const date = +echarts.time.parse(year + '-01-01');
  const end = +echarts.time.parse(year + '-12-31');
  const dayTime = 3600 * 24 * 1000;
  const data = [];
  for (let time = date; time <= end; time += dayTime) {
    data.push([
      echarts.time.format(time, '{yyyy}-{MM}-{dd}', false),
      Math.floor(Math.random() * 10000)
    ]);
  }
  return data;
}
option = {
  visualMap: {
    show: false,
    min: 0,
    max: 10000
  },
  calendar: {
    range: '2017'
  },
  series: {
    type: 'heatmap',
    coordinateSystem: 'calendar',
    data: getVirtualData('2017')
  }
};
```



## Key Points
- This is an official ECharts example from `calendar-simple/main.js`
- Template data format: `[[dateString, value], ...]  (dateString: 'YYYY-MM-DD')`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
