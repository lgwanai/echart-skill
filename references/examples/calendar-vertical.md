# 纵向日历图

**Category:** `'calendar, heatmap'`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=calendar-vertical
**Template:** examples/calendar-vertical.html
**Data Format:** `[[dateString, value], ...]  (dateString: 'YYYY-MM-DD')`
**Features:** visualMap component required

## Official Option Code

```javascript
/*
title: Calendar Heatmap Vertical
category: 'calendar, heatmap'
titleCN: 纵向日历图
shotWidth: 900
difficulty: 1
*/
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
    position: 'top',
    formatter: function (p) {
      const format = echarts.time.format(p.data[0], '{yyyy}-{MM}-{dd}', false);
      return format + ': ' + p.data[1];
    }
  },
  visualMap: {
    min: 0,
    max: 1000,
    calculable: true,
    orient: 'vertical',
    left: '670',
    top: 'center'
  },
  calendar: [
    {
      orient: 'vertical',
      range: '2015'
    },
    {
      left: 300,
      orient: 'vertical',
      range: '2016'
    },
    {
      left: 520,
      cellSize: [20, 'auto'],
      bottom: 10,
      orient: 'vertical',
      range: '2017',
      dayLabel: {
        margin: 5
      }
    }
  ],
  series: [
    {
      type: 'heatmap',
      coordinateSystem: 'calendar',
      calendarIndex: 0,
      data: getVirtualData('2015')
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
      data: getVirtualData('2017')
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py examples/calendar-vertical.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
