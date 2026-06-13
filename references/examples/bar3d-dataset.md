# ä½¿ç¨ dataset ä¸ºä¸ç»´æ±ç¶å¾è®¾ç½®æ°æ®

**Category:** `bar3D`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar3d-dataset
**Template:** NONE — use knowledge base
**Data Format:** `N/A`
**Features:** visualMap component required, uses encode (dataset dimension mapping), uses dataset (not series.data)

## Official Option Code

```javascript
/*
title: 3D Bar with Dataset
category: bar3D
titleCN: ä½¿ç¨ dataset ä¸ºä¸ç»´æ±ç¶å¾è®¾ç½®æ°æ®
*/
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

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
