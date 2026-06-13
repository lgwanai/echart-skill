# 断轴上的柱状图（可刷选） / Bar Chart with Axis Breaks (Brush-enabled)

**Category:** `bar`
**Example dir:** `bar-breaks-brush`

## Template
- **bar/basic.html** — Bar
Data format: `{ categories: string[], values: number[] }`

## Option Code
```javascript
var GRID_TOP = 120;
var GRID_BOTTOM = 80;
var Y_DATA_ROUND_PRECISION = 0;
var _currentAxisBreaks = [
  {
    start: 5000,
    end: 100000,
    gap: '2%'
  }
];
option = {
  title: {
    text: 'Bar Chart with Axis Break (Brush-enabled)',
    subtext:
      'Brush to create a new axis break.\nClick on the break area to reset.',
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
    top: GRID_TOP,
    bottom: GRID_BOTTOM
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
        zigzagMaxSpan: 15,
        zigzagAmplitude: 2,
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
      data: [106212, 102118, 102643, 104631, 106679, 100130, 107022],
      emphasis: {
        focus: 'series'
      }
    }
  ]
};

function initAxisBreakInteraction() {
  var _brushingEl = null;
  myChart.getZr().on('mousedown', function (params) {
    _brushingEl = new echarts.graphic.Rect({
      shape: { x: 0, y: params.offsetY },
      style: { stroke: 'none', fill: '#ccc' },
      ignore: true
    });
    myChart.getZr().add(_brushingE
```

## Key Points
- Generate via: `scripts/build_template.py bar/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
