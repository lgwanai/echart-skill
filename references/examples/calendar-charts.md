# 日历图 / Calendar Charts

**Category:** `'calendar, scatter'`
**Example dir:** `calendar-charts`

## Template
- **calendar/heatmap.html** — Calendar Heatmap
Data format: `[[dateString, value], ...]  (dateString: 'YYYY-MM-DD')`

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
const graphData = [
  ['2017-02-01', 260],
  ['2017-02-04', 200],
  ['2017-02-09', 279],
  ['2017-02-13', 847],
  ['2017-02-18', 241],
  ['2017-02-23', 411],
  ['2017-02-27', 985]
];
const links = graphData.map(function (item, idx) {
  return {
    source: idx,
    target: idx + 1
  };
});
links.pop();
option = {
  tooltip: {
    position: 'top'
  },
  visualMap: [
    {
      min: 0,
      max: 1000,
      calculable: true,
      seriesIndex: [2, 3, 4],
      orient: 'horizontal',
      left: '55%',
      bottom: 20
    },
    {
      min: 0,
      max: 1000,
      inRange: {
        color: ['grey'],
        opacity: [0, 0.3]
      },
      controller: {
        inRange: {
          opacity: [0.3, 0.6]
        },
        outOfRange: {
          color: '#ccc'
        }
      },
      seriesIndex: [1],
      orient: 'horizontal',
      left: '10%',
      bottom: 20
    }
  ],
  calendar: [
    {
      orient: 'vertical',
      yearLabel: {
        margin: 40
      },
      monthLabel: {
        nameMap: 'cn',
        margin: 20
      },
      dayLabel: {
        firstDay: 1,
        nameMap: 'cn'
      },
      cellSize: 40,
      range: '2017-02'
    },
    {
      orient: 'vertical',
      yearLabel: {
        margin: 40
      },
      monthLabel: {
        margin: 20
      },
      cellSize: 40,
      left: 460,
      range: '2017-01'
    },
    {
      orient: 'vertical',
      yearLabel: {
        margin: 40
      },
      monthLabel: {
        margin: 20
      },
      cellSize: 40,
      top: 350,
      range: '2017-03'
    },
    {
      orient: 'vertical',
      yearLab
```

## Key Points
- Generate via: `scripts/build_template.py calendar/heatmap.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
