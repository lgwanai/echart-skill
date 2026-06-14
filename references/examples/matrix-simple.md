# matrix-simple

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=matrix-simple
**Chart Type:** `continuous`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

Data arrays to replace: **3**

## Reference Code

```javascript
/*
title: Simple Matrix
category: matrix
titleCN: 简单的矩阵图
difficulty: 1
since: 6.0.0
*/
option = {
  matrix: {
    x: {
      data: [
        {
          value: 'A',
          children: [
            'A1',
            'A2',
            {
              value: 'A3',
              children: ['A31', 'A32']
            }
          ]
        }
      ]
    },
    y: {
      data: ['U', 'V']
    },
    top: 150,
    bottom: 150
  },
  visualMap: {
    type: 'continuous',
    min: 0,
    max: 80,
    top: 'middle',
    dimension: 2,
    calculable: true
  },
  series: {
    type: 'heatmap',
    coordinateSystem: 'matrix',
    data: [
      ['A1', 'U', 10],
      ['A1', 'V', 20],
      ['A2', 'U', 30],
      ['A2', 'V', 40],
      ['A31', 'U', 50],
      ['A3', 'V', 60]
    ],
    label: {
      show: true
    }
  }
};
```
