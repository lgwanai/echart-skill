# calendar-heatmap

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=calendar-heatmap

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Calendar Heatmap
category: 'calendar, heatmap'
titleCN: 日历热力图
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
      Math.floor(Math.random() * 10000)
    ]);
  }
  return data;
}
option = {
  title: {
    top: 30,
    left: 'center',
    text: 'Daily Step Count'
  },
  tooltip: {},
  visualMap: {
    min: 0,
    max: 10000,
    type: 'piecewise',
    orient: 'horizontal',
    left: 'center',
    top: 65
  },
  calendar: {
    top: 120,
    left: 30,
    right: 30,
    cellSize: ['auto', 13],
    range: '2016',
    itemStyle: {
      borderWidth: 0.5
    },
    yearLabel: { show: false }
  },
  series: {
    type: 'heatmap',
    coordinateSystem: 'calendar',
    data: getVirtualData('2016')
  }
};
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
