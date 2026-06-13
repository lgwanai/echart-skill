# ä½¿ç¨ dataset ä¸ºä¸ç»´æ£ç¹å¾è®¾ç½®æ°æ® / 3D Scatter with Dataset

**Category:** `scatter3D`
**Example dir:** `scatter3D-dataset`

## Template
⚠️ No template — use knowledge base
Data format: `N/A`

## Option Code
```javascript
$.get(
  ROOT_PATH + '/data/asset/data/life-expectancy-table.json',
  function (data) {
    var symbolSize = 2.5;
    option = {
      grid3D: {},
      xAxis3D: {
        type: 'category'
      },
      yAxis3D: {},
      zAxis3D: {},
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
          symbolSize: symbolSize,
          encode: {
            x: 'Country',
            y: 'Life Expectancy',
            z: 'Income',
            tooltip: [0, 1, 2, 3, 4]
          }
        }
      ]
    };
    myChart.setOption(option);
  }
);
```

## Key Points
- Generate via: `scripts/build_template.py  -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
