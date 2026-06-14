# radar-multiple

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=radar-multiple
**Chart Type:** `radar`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: need **name** + multiple **dimension** columns
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

Data arrays to replace: **4**

## Reference Code

```javascript
/*
title: Multiple Radar
category: radar
titleCN: 多雷达图
*/
option = {
  title: {
    text: 'Multiple Radar'
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    left: 'center',
    data: [
      'A Software',
      'A Phone',
      'Another Phone',
      'Precipitation',
      'Evaporation'
    ]
  },
  radar: [
    {
      indicator: [
        { text: 'Brand', max: 100 },
        { text: 'Content', max: 100 },
        { text: 'Usability', max: 100 },
        { text: 'Function', max: 100 }
      ],
      center: ['25%', '40%'],
      radius: 80
    },
    {
      indicator: [
        { text: 'Look', max: 100 },
        { text: 'Photo', max: 100 },
        { text: 'System', max: 100 },
        { text: 'Performance', max: 100 },
        { text: 'Screen', max: 100 }
      ],
      radius: 80,
      center: ['50%', '60%']
    },
    {
      indicator: (function () {
        var res = [];
        for (var i = 1; i <= 12; i++) {
          res.push({ text: i + '月', max: 100 });
        }
        return res;
      })(),
      center: ['75%', '40%'],
      radius: 80
    }
  ],
  series: [
    {
      type: 'radar',
      tooltip: {
        trigger: 'item'
      },
      areaStyle: {},
      data: [
        {
          value: [60, 73, 85, 40],
          name: 'A Software'
        }
      ]
    },
    {
      type: 'radar',
      radarIndex: 1,
      areaStyle: {},
      data: [
        {
          value: [85, 90, 90, 95, 95],
          name: 'A Phone'
        },
        {
          value: [95, 80, 95, 90, 93],
          name: 'Another Phone'
        }
      ]
    },
    {
      type: 'radar',
      radarIndex: 2,
      areaStyle: {},
      data: [
        {
          name: 'Precipitation',
          value: [
            2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 75.6, 82.2, 48.7, 18.8, 6.0, 2.3
          ]
        },
        {
          name: 'Evaporation',
          value: [
            2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 35.6, 62.2, 32.6, 20.0, 6.4, 3.3
          ]
        }
      ]
    }
  ]
};
```
