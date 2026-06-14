# bar3d-dataset

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar3d-dataset
**Chart Type:** `category`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

## Reference Code

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
