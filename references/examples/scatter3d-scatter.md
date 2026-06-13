# ä¸ç»´æ£ç¹å¾åæ£ç¹ç©éµç»åä½¿ç¨ / 3D Scatter with Scatter Matrix

**Category:** `scatter3D`
**Example dir:** `scatter3d-scatter`

## Template
- **3d/scatter3d.html** — Scatter3D
Data format: `[[x, y, z], ...]`

## Option Code
```javascript
$.get(
  ROOT_PATH + '/data/asset/data/life-expectancy-table.json',
  function (data) {
    var sizeValue = '57%';
    var symbolSize = 2.5;
    option = {
      tooltip: {},
      grid3D: {
        width: '50%'
      },
      xAxis3D: {},
      yAxis3D: {},
      zAxis3D: {},
      grid: [
        { left: '50%', width: '20%', bottom: sizeValue },
        { left: '75%', width: '20%', bottom: sizeValue },
        { left: '50%', width: '20%', top: sizeValue },
        { left: '75%', width: '20%', top: sizeValue }
      ],
      xAxis: [
        {
          type: 'value',
          gridIndex: 0,
          name: 'Income',
          axisLabel: { rotate: 50, interval: 0 }
        },
        {
          type: 'category',
          gridIndex: 1,
          name: 'Country',
          boundaryGap: false,
          axisLabel: { rotate: 50, interval: 0 }
        },
        {
          type: 'value',
          gridIndex: 2,
          name: 'Income',
          axisLabel: { rotate: 50, interval: 0 }
        },
        {
          type: 'value',
          gridIndex: 3,
          name: 'Life Expectancy',
          axisLabel: { rotate: 50, interval: 0 }
        }
      ],
      yAxis: [
        { type: 'value', gridIndex: 0, name: 'Life Expectancy' },
        { type: 'value', gridIndex: 1, name: 'Income' },
        { type: 'value', gridIndex: 2, name: 'Population' },
        { type: 'value', gridIndex: 3, name: 'Population' }
      ],
      dataset: {
        dimensions: [
          'Income',
          'Life Expectancy',
          'Population',
          'Country',
          { name: 'Year', type: 'ordinal' }
        ],
        source: data
      },
      series: [
        {
          type: 'scatter3D',
          symbolSize: 3,
          encode: {
            x: 'Population',
            y: 'Life Expectancy',
            z: 'Income',
            tooltip: [0, 1, 2, 3, 4]
          }
        },
        {
          type: 'scatter',
          symbolSize: symbolSize,
          xAxisIndex: 0
```

## Key Points
- Generate via: `scripts/build_template.py 3d/scatter3d.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
