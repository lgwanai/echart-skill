# chord-style

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=chord-style
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
title: Chord Style
category: chord
titleCN: 和弦图样式
difficulty: 10
since: 6.0.0
*/
option = {
  tooltip: {},
  legend: {},
  series: [
    {
      type: 'chord',
      padAngle: 1,
      center: ['50%', '48%'],
      radius: ['70%', '80%'],
      data: [
        { name: 'A' },
        { name: 'B' },
        { name: 'C' },
        { name: 'D' },
        { name: 'E' },
        { name: 'F' },
        { name: 'G' }
      ],
      itemStyle: {
        borderRadius: [0, 15],
        borderWidth: 2,
        borderColor: '#fff'
      },
      lineStyle: {
        opacity: 0.3,
        color: 'gradient' // or 'source' (default), 'target'
      },
      emphasis: {
        focus: 'self' // or 'none', 'adjacency' (default)
      },
      label: {
        show: true,
        position: 'inside',
        color: '#fff',
        fontWeight: 'bold'
      },
      links: [
        { source: 'A', target: 'B', value: 14 },
        { source: 'A', target: 'C', value: 8 },
        { source: 'B', target: 'C', value: 20 },
        { source: 'B', target: 'E', value: 15 },
        { source: 'C', target: 'B', value: 8 },
        { source: 'C', target: 'E', value: 3 },
        { source: 'D', target: 'A', value: 12 },
        { source: 'D', target: 'B', value: 3 },
        { source: 'E', target: 'A', value: 15 },
        { source: 'E', target: 'C', value: 5 },
        { source: 'F', target: 'C', value: 5 },
        { source: 'G', target: 'A', value: 6 },
        { source: 'G', target: 'B', value: 8 },
        { source: 'G', target: 'D', value: 4 }
      ]
    }
  ]
};
```
