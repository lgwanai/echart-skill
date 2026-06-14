# chord-minAngle

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=chord-minAngle
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
title: Chord minAngle
category: chord
titleCN: 和弦图 minAngle
difficulty: 1
since: 6.0.0
*/
option = {
  tooltip: {},
  legend: {},
  series: [
    {
      type: 'chord',
      label: { show: true },
      minAngle: 30,
      data: [
        { name: 'A' },
        { name: 'B' },
        { name: 'C' },
        { name: 'D' },
        { name: 'E' },
        { name: 'F' }
      ],
      links: [
        { source: 'A', target: 'B', value: 40 },
        { source: 'B', target: 'C', value: 20 },
        { source: 'E', target: 'A', value: 5 }
      ]
    }
  ]
};
```
