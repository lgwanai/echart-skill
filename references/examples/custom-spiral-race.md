# 自定义螺旋线竞速 / Custom Spiral Race

**Category:** `custom`
**Example dir:** `custom-spiral-race`

## Template
- **custom/error-bar.html** — Error Bar
Data format: `[[xIdx, val, lowVal, highVal], ...]`

## Option Code
```javascript
var _animationDuration = 5000;
var _animationDurationUpdate = 7000;
var _animationEasingUpdate = 'linear';
// prettier-ignore
var _radianLabels = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpius', 'Sagittarius', 'Capricornus', 'Aquarius', 'Pisces'];
var _valOnRoundRadian = _radianLabels.length;
var _radianStep = Math.PI / 45;
var _barWidthValue = 0.4;
var _valOnRadiusStep = 4;
// angleAxis.startAngle is 90 by default.
var _startRadian = Math.PI / 2;
// prettier-ignore
var _colors = [
    { fill: '#5470c6', text: '#2747a5' },
    { fill: '#91cc75', text: '#447f27' },
    { fill: '#fac858', text: '#a0761c' }
];
var _currentDataIndex = 0;
// prettier-ignore
var _datasourceList = [
    [[1, 3], [2, 6], [3, 9]],
    [[1, 12], [2, 16], [3, 14]],
    [[1, 17], [2, 22], [3, 19]],
    [[1, 19], [2, 33], [3, 24]],
    [[1, 24], [2, 42], [3, 29]],
    [[1, 27], [2, 47], [3, 41]],
    [[1, 36], [2, 52], [3, 52]],
    [[1, 46], [2, 59], [3, 63]],
    [[1, 60], [2, 63], [3, 69]],
];
var _barNamesByOrdinal = { 1: 'A', 2: 'B', 3: 'C' };
function getMaxRadius() {
  var radius = 0;
  var datasource = _datasourceList[_currentDataIndex];
  for (var j = 0; j < datasource.length; j++) {
    var dataItem = datasource[j];
    radius = Math.max(radius, getSpiralValueOnRadius(dataItem[0], dataItem[1]));
  }
  return Math.ceil(radius * 1.2);
}
function getSpiralValueOnRadius(valOnStartRadius, valOnEndAngle) {
  return (
    valOnStartRadius + _valOnRadiusStep * (valOnEndAngle / _valOnRoundRadian)
  );
}
function getSpiralRadius(startRadius, endRadian, radiusStep) {
  return (
    startRadius + radiusStep * ((_startRadian - endRadian) / (Math.PI * 2))
  );
}
function renderItem(params, api) {
  var children = [];
  var dataIdx = params.dataIndex;
  addShapes(
    params,
    api,
    children,
    api.value(0),
    api.value(1),
    _colors[dataIdx]
  );
  return {
    type: 'group',
    children: children
  };
}
function addShapes(
  params,
  api,
  children,
  valO
```

## Key Points
- Generate via: `scripts/build_template.py custom/error-bar.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
