# 散点图变形动画 / Symbol Shape Morph

**Category:** `scatter`
**Example dir:** `scatter-symbol-morph`

## Template
- **scatter/basic.html** — Scatter
Data format: `[[x, y], [x, y], ...]`

## Option Code
```javascript
let xData = [];
let yData = [];
let data = [];
for (let y = 0; y < 10; y++) {
  yData.push(y);
  for (let x = 0; x < 10; x++) {
    data.push([x, y, 10]);
  }
}
for (let x = 0; x < 10; x++) {
  xData.push(x);
}
const options = [
  {
    grid: {
      left: 0,
      right: 0,
      top: 0,
      bottom: 0
    },
    xAxis: {
      show: false,
      type: 'category',
      data: xData
    },
    yAxis: {
      show: false,
      type: 'category',
      data: yData
    },
    series: [
      {
        type: 'scatter',
        data: data,
        symbol: 'roundRect',
        symbolKeepAspect: true,
        universalTransition: true,
        symbolSize: 50
      }
    ]
  },
  {
    series: [
      {
        type: 'scatter',
        symbol: 'circle'
      }
    ]
  },
  {
    // heart
    series: [
      {
        symbol:
          'path://M23.6 2c-3.363 0-6.258 2.736-7.599 5.594-1.342-2.858-4.237-5.594-7.601-5.594-4.637 0-8.4 3.764-8.4 8.401 0 9.433 9.516 11.906 16.001 21.232 6.13-9.268 15.999-12.1 15.999-21.232 0-4.637-3.763-8.401-8.4-8.401z'
      }
    ]
  },
  {
    // happy
    series: [
      {
        symbol:
          'path://M16 0c-8.837 0-16 7.163-16 16s7.163 16 16 16 16-7.163 16-16-7.163-16-16-16zM22 8c1.105 0 2 1.343 2 3s-0.895 3-2 3-2-1.343-2-3 0.895-3 2-3zM10 8c1.105 0 2 1.343 2 3s-0.895 3-2 3-2-1.343-2-3 0.895-3 2-3zM16 28c-5.215 0-9.544-4.371-10-9.947 2.93 1.691 6.377 2.658 10 2.658s7.070-0.963 10-2.654c-0.455 5.576-4.785 9.942-10 9.942z'
      }
    ]
  },
  {
    // evil
    series: [
      {
        symbol:
          'path://M32 2c0-1.422-0.298-2.775-0.833-4-1.049 2.401-3.014 4.31-5.453 5.287-2.694-2.061-6.061-3.287-9.714-3.287s-7.021 1.226-9.714 3.287c-2.439-0.976-4.404-2.886-5.453-5.287-0.535 1.225-0.833 2.578-0.833 4 0 2.299 0.777 4.417 2.081 6.106-1.324 2.329-2.081 5.023-2.081 7.894 0 8.837 7.163 16 16 16s16-7.163 16-16c0-2.871-0.757-5.565-2.081-7.894 1.304-1.689 2.081-3.806 2.081-6.106zM18.003 11.891c0.064-1.483 1.413-2.467 2.55-3.036 1.086-0.54
```

## Key Points
- Generate via: `scripts/build_template.py scatter/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
