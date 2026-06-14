# matrix-covariance

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=matrix-covariance
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

## Reference Code

```javascript
/*
title: Covariance Matrix
category: matrix
titleCN: 协方差矩阵
difficulty: 2
since: 6.0.0
*/
const xData = [];
const yData = [];
for (let i = 0; i < 5; ++i) {
  const children = [];
  for (let j = 0; j < 5; ++j) {
    children.push(i * 5 + j + 1 + '');
  }
  xData.push({
    value: 'X' + (i + 1),
    children
  });
  yData.push({
    value: 'Y' + (i + 1),
    children
  });
}
const data = [];
const size = 25;
let temp = {};
for (let i = 1; i <= size; ++i) {
  for (let j = 1; j <= size; ++j) {
    let base = i === j ? 100 : 20;
    const iGroup = Math.ceil(i / 5);
    const jGroup = Math.ceil(j / 5);
    base += (3 - Math.abs(iGroup - jGroup)) * 35;
    if (i % 5 === j % 5) {
      base += 20;
    }
    if (Math.random() > 0.9) {
      base += Math.random() * 40;
    }
    if (i > j) {
      // Use the previously calculated value to ensure symmetry
      data.push([i + '', j + '', temp[j + '_' + i]]);
    } else {
      // Calculate a new value and save it for future use
      let value = (Math.random() * 0.5 + 0.5) * base;
      data.push([i + '', j + '', value]);
      temp[i + '_' + j] = value;
    }
  }
}
option = {
  matrix: {
    x: {
      data: xData,
      show: false
    },
    y: {
      data: yData,
      show: false
    },
    width: 500,
    height: 500,
    left: (window.innerWidth - 500) / 2
  },
  tooltip: {
    show: true,
    valueFormatter: (value) => Math.round(value)
  },
  visualMap: {
    type: 'continuous',
    min: 15,
    max: 120,
    dimension: 2,
    calculable: true,
    orient: 'horizontal',
    top: 5,
    left: 'center',
    inRange: {
      color: [
        '#313695',
        '#4575b4',
        '#74add1',
        '#abd9e9',
        '#e0f3f8',
        '#ffffbf',
        '#fee090',
        '#fdae61',
        '#f46d43',
        '#d73027',
        '#a50026'
      ]
    }
  },
  series: {
    type: 'heatmap',
    coordinateSystem: 'matrix',
    data
  }
};
```
