# ä½¿ç¨ dataset ä¸ºä¸ç»´æ±ç¶å¾è®¾ç½®æ°æ® / 3D Bar with Dataset

**Category:** `bar3D`
**Example dir:** `bar3d-dataset`

## Template
- **3d/bar3d.html** — Bar3D
Data format: `[[x, y, z], ...]`

## Option Code
```javascript
$.get(
  ROOT_PATH + '/data/asset/data/life-expectancy-table.json',
  function (data) {
    option = {
      grid3D: {},
      tooltip: {},
      xAxis3D: {
        type: 'category'
      },
      yAxis3D: {
        type: 'category'
      },
      zAxis3D: {},
      visualMap: {
        max: 1e8,
        dimension: 'Population'
      },
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
          type: 'bar3D',
          // symbolSize: symbolSize,
          shading: 'lambert',
          encode: {
            x: 'Year',
            y: 'Country',
            z: 'Life Expectancy',
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
- Generate via: `scripts/build_template.py 3d/bar3d.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
