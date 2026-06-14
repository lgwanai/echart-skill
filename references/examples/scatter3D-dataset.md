# ä½¿ç¨ dataset ä¸ºä¸ç»´æ£ç¹å¾è®¾ç½®æ°æ®

**Category:** `scatter3D`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter3D-dataset
**Template:** examples/scatter3D-dataset.html
**Data Format:** `N/A`
**Features:** uses encode (dataset dimension mapping), uses dataset (not series.data)

## Official Option Code

```javascript
/*
title: 3D Scatter with Dataset
category: scatter3D
titleCN: ä½¿ç¨ dataset ä¸ºä¸ç»´æ£ç¹å¾è®¾ç½®æ°æ®
*/
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

## Placeholders

| Placeholder | Type | Description |
|-------------|------|-------------|
| `{{{TITLE}}}` | string | title |

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
