# 断轴上的柱状图 / Bar Chart with Axis Breaks

**Category:** `bar`
**Example dir:** `bar-breaks-simple`

## Template
- **bar/basic.html** — Bar
Data format: `{ categories: string[], values: number[] }`

## Option Code
```javascript
var _currentAxisBreaks = [
  {
    start: 5000,
    end: 100000,
    gap: '1.5%'
  },
  {
    // `start` and `end` are also used as the identifier for a certain axis break.
    start: 105000,
    end: 3100000,
    gap: '1.5%'
  }
];
option = {
  title: {
    text: 'Bar Chart with Axis Breaks',
    subtext: 'Click the break area to expand it',
    left: 'center',
    textStyle: {
      fontSize: 20
    },
    subtextStyle: {
      color: '#175ce5',
      fontSize: 15,
      fontWeight: 'bold'
    }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {},
  grid: {
    top: 120
  },
  xAxis: [
    {
      type: 'category',
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    }
  ],
  yAxis: [
    {
      type: 'value',
      breaks: _currentAxisBreaks,
      breakArea: {
        itemStyle: {
          opacity: 1
        },
        zigzagZ: 200
      }
    }
  ],
  series: [
    {
      name: 'Data A',
      type: 'bar',
      emphasis: {
        focus: 'series'
      },
      data: [1500, 2032, 2001, 3154, 2190, 4330, 2410]
    },
    {
      name: 'Data B',
      type: 'bar',
      emphasis: {
        focus: 'series'
      },
      data: [1200, 1320, 1010, 1340, 900, 2300, 2100]
    },
    {
      name: 'Data C',
      type: 'bar',
      emphasis: {
        focus: 'series'
      },
      data: [103200, 100320, 103010, 102340, 103900, 103300, 103200]
    },
    {
      name: 'Data D',
      type: 'bar',
      data: [3106212, 3102118, 3102643, 3104631, 3106679, 3100130, 3107022],
      emphasis: {
        focus: 'series'
      }
    }
  ]
};

function initAxisBreakInteraction() {
  myChart.on('axisbreakchanged', function (params) {
    updateCollapseButton(params);
  });
  myChart.on('click', function (params) {
    if (params.name === 'collapseAxisBreakBtn') {
      collapseAxisBreak();
    }
  });
  function updateCollapseButton(params) {
    // If there is any axis break expanded, we need to show the collap
```

## Key Points
- Generate via: `scripts/build_template.py bar/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
