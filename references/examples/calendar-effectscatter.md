# calendar-effectscatter

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=calendar-effectscatter
**Chart Type:** `solid`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

Data arrays to replace: **1**

## Reference Code

```javascript
/*
title: Calendar EffectScatter
category: calendar
titleCN: 热力特效散点图
difficulty:3
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
const data = getVirtualData('2016');
option = {
  backgroundColor: '#404a59',
  title: {
    top: 30,
    text: 'Daily Step Count in 2016',
    subtext: 'Fake Data',
    left: 'center',
    textStyle: {
      color: '#fff'
    }
  },
  tooltip: {
    trigger: 'item'
  },
  legend: {
    top: '30',
    left: '100',
    data: ['Steps', 'Top 12'],
    textStyle: {
      color: '#fff'
    }
  },
  calendar: [
    {
      top: 120,
      left: 'center',
      range: ['2016-01-01', '2016-06-30'],
      splitLine: {
        show: true,
        lineStyle: {
          color: '#000',
          width: 4,
          type: 'solid'
        }
      },
      yearLabel: {
        formatter: '{start}  1st',
        color: '#fff'
      },
      monthLabel: {
        color: '#aaa'
      },
      dayLabel: {
        color: '#aaa'
      },
      itemStyle: {
        color: '#323c48',
        borderWidth: 1,
        borderColor: '#111'
      }
    },
    {
      top: 340,
      left: 'center',
      range: ['2016-07-01', '2016-12-31'],
      splitLine: {
        show: true,
        lineStyle: {
          color: '#000',
          width: 4,
          type: 'solid'
        }
      },
      yearLabel: {
        formatter: '{start}  2nd',
        color: '#fff'
      },
      monthLabel: {
        color: '#aaa'
      },
      dayLabel: {
        color: '#aaa'
      },
      itemStyle: {
        color: '#323c48',
        borderWidth: 1,
        borderColor: '#111'
      }
    }
  ],
  series: [
    {
      name: 'Steps',
      type: 'scatter',
      coordinateSystem: 'calendar',
      data: data,
      symbolSize: function (val) {
        return val[1] / 500;
      },
      itemStyle: {
        color: '#ddb926'
      }
    },
    {
      name: 'Steps',
      type: 'scatter',
      coordinateSystem: 'calendar',
      calendarIndex: 1,
      data: data,
      symbolSize: function (val) {
        return val[1] / 500;
      },
      itemStyle: {
        color: '#ddb926'
      }
    },
    {
      name: 'Top 12',
      type: 'effectScatter',
      coordinateSystem: 'calendar',
      calendarIndex: 1,
      data: data
        .sort(function (a, b) {
          return b[1] - a[1];
        })
        .slice(0, 12),
      symbolSize: function (val) {
        return val[1] / 500;
      },
      showEffectOn: 'render',
      rippleEffect: {
        brushType: 'stroke'
      },
      itemStyle: {
        color: '#f4e925',
        shadowBlur: 10,
        shadowColor: '#333'
      },
      zlevel: 1
    },
    {
      name: 'Top 12',
      type: 'effectScatter',
      coordinateSystem: 'calendar',
      data: data
        .sort(function (a, b) {
          return b[1] - a[1];
        })
        .slice(0, 12),
      symbolSize: function (val) {
        return val[1] / 500;
      },
      showEffectOn: 'render',
      rippleEffect: {
        brushType: 'stroke'
      },
      itemStyle: {
        color: '#f4e925',
        shadowBlur: 10,
        shadowColor: '#333'
      },
      zlevel: 1
    }
  ]
};
```
