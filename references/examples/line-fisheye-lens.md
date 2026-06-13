# 折线图鱼眼放大 / Fisheye Lens on Line Chart

**Category:** `line`
**Example dir:** `line-fisheye-lens`

## Template
- **line/basic.html** — Line
Data format: `{ categories: string[], values: number[] }`

## Option Code
```javascript
var GRID_TOP = 120;
var GRID_BOTTOM = 80;
var GRID_LEFT = 60;
var GRID_RIGHT = 60;
var Y_DATA_ROUND_PRECISION = 0;
var _breakAreaStyle = {
  expandOnClick: false,
  zigzagZ: 200,
  zigzagAmplitude: 0,
  itemStyle: {
    borderColor: '#777',
    opacity: 0
  }
};
option = {
  title: {
    text: 'Fisheye Lens on Line Chart',
    subtext: 'Brush to magnify the details',
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
    trigger: 'axis'
  },
  legend: {},
  grid: {
    top: GRID_TOP,
    bottom: GRID_BOTTOM,
    left: GRID_LEFT,
    right: GRID_RIGHT
  },
  xAxis: [
    {
      splitLine: {
        show: false
      },
      breakArea: _breakAreaStyle
    }
  ],
  yAxis: [
    {
      axisTick: {
        show: true
      },
      breakArea: _breakAreaStyle
    }
  ],
  series: [
    {
      type: 'line',
      name: 'Data A',
      symbol: 'circle',
      showSymbol: false,
      symbolSize: 5,
      data: generateSeriesData()
    }
  ]
};

function initAxisBreakInteraction() {
  var _brushingEl = null;
  myChart.on('click', function (params) {
    if (params.name === 'clearAxisBreakBtn') {
      var option = {
        xAxis: { breaks: [] },
        yAxis: { breaks: [] }
      };
      addClearButtonUpdateOption(option, false);
      myChart.setOption(option);
    }
  });
  function addClearButtonUpdateOption(option, show) {
    option.graphic = [
      {
        elements: [
          {
            type: 'rect',
            ignore: !show,
            name: 'clearAxisBreakBtn',
            top: 5,
            left: 5,
            shape: { r: 3, width: 70, height: 30 },
            style: { fill: '#eee', stroke: '#999', lineWidth: 1 },
            textContent: {
              type: 'text',
              style: {
                text: 'Reset',
                fontSize: 15,
                fontWeight: 'bold'
              }
            },
        
```

## Key Points
- Generate via: `scripts/build_template.py line/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
