# 矩阵坐标系下的微型条形图和地图 / Mini Bars and Geo in Matrix

**Category:** `matrix, bar, geo`
**Example dir:** `matrix-mini-bar-geo`

## Template
⚠️ No template — use knowledge base
Data format: `N/A`

## Option Code
```javascript
var _colHeaders = ['Region and Time', 'Data A', 'Data B', 'Location'];
var _regionColIdx = 0;
var _geoColIdx = 3;
var _dataSourceList = [
  {
    name: '2021',
    data: [
      // 'Region', 'Data A', 'Data B'
      ['Valais', 1212, 2321],
      ['Ticino', 7181, 2114],
      ['Graubünden', 2763, 4212],
      ['Uri', 6122, 2942],
      ['Lucerne', 4221, 3411],
      ['Neuchâtel', 7221, 5121],
      ['Jura', 5121, 4121],
      ['Vaud', 6121, 3121],
      ['Thurgau', 7121, 2121],
      ['Schwyz', 8121, 1121]
    ]
  },
  {
    name: '2020',
    data: [
      // 'Region', 'Data A', 'Data B'
      ['Valais', 1010, 2221],
      ['Ticino', 7040, 1810],
      ['Graubünden', 2313, 4011],
      ['Uri', 6011, 2749],
      ['Lucerne', 3329, 3015],
      ['Neuchâtel', 7116, 4822],
      ['Jura', 4968, 3820],
      ['Vaud', 6027, 2928],
      ['Thurgau', 7011, 1725],
      ['Schwyz', 7311, 825]
    ]
  }
];
var _colorList = [
  '#ffd10a',
  '#0ca8df',
  '#b6d634',
  '#3fbe95',
  '#5070dd',
  '#ff994d',
  '#505372',
  '#fb628b',
  '#785db0'
];
function createChart() {
  option = {
    matrix: {
      x: {
        levelSize: 40,
        data: _colHeaders.map(function (item, colIdx) {
          return {
            value: item,
            size:
              colIdx === _geoColIdx
                ? '15%'
                : colIdx === _regionColIdx
                ? 120
                : undefined
          };
        }),
        itemStyle: { color: '#f0f8ff' },
        label: { fontWeight: 'bold' }
      },
      y: {
        data: _dataSourceList[0].data.map(function () {
          return '_'; // Any value is fine here, as we will not use it.
        }),
        show: false
      },
      body: {
        data: []
      },
      top: 25
    },
    legend: {},
    tooltip: {},
    grid: [],
    xAxis: [],
    yAxis: [],
    geo: [],
    series: []
  };
  // Assume every dataSourceList[i] has the same length; just for simplicity in this demo.
  var rowCount = _dataSourceList[0].data.le
```

## Key Points
- Generate via: `scripts/build_template.py  -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
