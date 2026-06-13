# 矩阵中的微型折线图 / Mini Line Charts (Sparkline) in Matrix

**Category:** `matrix, line`
**Example dir:** `matrix-sparkline`

## Template
⚠️ No template — use knowledge base
Data format: `N/A`

## Option Code
```javascript
const _matrixDimensionData = {
  x: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
  y: [
    { value: '8:00\n~\n10:00' },
    { value: '10:00\n~\n12:00' },
    { value: '12:00\n~\n14:00', size: 55 },
    { value: '14:00\n~\n16:00' },
    { value: '16:00\n~\n18:00' },
    { value: '18:00\n~\n20:00' }
  ]
};
const _yBreakTimeIndex = 2; // '12:00 - 14:00',
const _seriesFakeDataLength = 365;
option = {
  matrix: {
    x: {
      data: _matrixDimensionData.x,
      levelSize: 40,
      label: {
        fontSize: 16,
        color: '#555'
      }
    },
    y: {
      data: _matrixDimensionData.y,
      levelSize: 70,
      label: {
        fontSize: 14,
        color: '#777'
      }
    },
    corner: {
      data: [
        {
          coord: [-1, -1],
          value: 'Time'
        }
      ],
      label: {
        fontSize: 16,
        color: '#777'
      }
    },
    body: {
      data: [
        {
          coord: [null, _yBreakTimeIndex],
          coordClamp: true,
          mergeCells: true,
          value: 'Break',
          label: {
            color: '#999',
            fontSize: 16
          }
        }
      ]
    },
    top: 30,
    bottom: 80,
    width: '90%',
    left: 'center'
  },
  tooltip: {
    trigger: 'axis'
  },
  dataZoom: [
    {
      type: 'slider',
      xAxisIndex: 'all',
      left: '10%',
      right: '10%',
      bottom: 30,
      height: 30,
      throttle: 120
    },
    {
      type: 'inside',
      xAxisIndex: 'all',
      throttle: 120
    }
  ],
  grid: [],
  xAxis: [],
  yAxis: [],
  series: []
};
eachMatrixCell((xval, yval, xidx, yidx) => {
  const id = makeId(xidx, yidx);
  option.grid.push({
    id: id,
    coordinateSystem: 'matrix',
    coord: [xval, yval],
    top: 10,
    bottom: 10,
    left: 'center',
    width: '90%',
    containLabel: true
  });
  option.xAxis.push({
    type: 'category',
    id: id,
    gridId: id,
    scale: true,
    axisTick: { show: false },
    axisLabel: { show: false },
    axisLine: { show: false },
 
```

## Key Points
- Generate via: `scripts/build_template.py  -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
