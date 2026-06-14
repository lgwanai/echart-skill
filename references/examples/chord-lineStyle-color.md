# chord-lineStyle-color

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=chord-lineStyle-color
**Chart Type:** `chord`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

Data arrays to replace: **1**

## Reference Code

```javascript
/*
title: Chord lineStyle.color
category: chord
titleCN: 和弦图边的颜色
difficulty: 3
since: 6.0.0
*/
function generateSeries(id, lineColor) {
  return {
    type: 'chord',
    label: { show: true },
    center: [((id * 2 + 1) / 6) * 100 + '%', '50%'],
    radius: ['28%', '32%'],
    lineStyle: {
      color: lineColor
    },
    data: [{ name: 'A' }, { name: 'B' }, { name: 'C' }, { name: 'D' }],
    links: [
      { source: 'A', target: 'B', value: 30 },
      { source: 'A', target: 'C', value: 20 },
      { source: 'B', target: 'D', value: 10 },
      { source: 'C', target: 'A', value: 15 },
      { source: 'D', target: 'A', value: 25 }
    ]
  };
}
function generateTitle(id, text) {
  return {
    text,
    left: ((id * 2 + 1) / 6) * 100 + '%',
    top: '25%',
    textAlign: 'center',
    padding: 0
  };
}
option = {
  tooltip: {},
  legend: {},
  series: [
    generateSeries(0, 'source'),
    generateSeries(1, 'target'),
    generateSeries(2, 'gradient')
  ],
  title: [
    {
      text: 'lineStyle.color',
      textStyle: {
        fontSize: 24
      }
    },
    generateTitle(0, 'source'),
    generateTitle(1, 'target'),
    generateTitle(2, 'gradient')
  ]
};
```
