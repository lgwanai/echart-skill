# sankey-vertical

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sankey-vertical
**Chart Type:** `sankey`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: need **source**, **target**, **value** columns
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

Data arrays to replace: **1**

## Reference Code

```javascript
/*
title: Sankey Orient Vertical
category: sankey
titleCN: 垂直方向的桑基图
difficulty: 1
*/
option = {
  tooltip: {
    trigger: 'item',
    triggerOn: 'mousemove'
  },
  animation: false,
  series: [
    {
      type: 'sankey',
      bottom: '10%',
      emphasis: {
        focus: 'adjacency'
      },
      data: [
        { name: 'a' },
        { name: 'b' },
        { name: 'a1' },
        { name: 'b1' },
        { name: 'c' },
        { name: 'e' }
      ],
      links: [
        { source: 'a', target: 'a1', value: 5 },
        { source: 'e', target: 'b', value: 3 },
        { source: 'a', target: 'b1', value: 3 },
        { source: 'b1', target: 'a1', value: 1 },
        { source: 'b1', target: 'c', value: 2 },
        { source: 'b', target: 'c', value: 1 }
      ],
      orient: 'vertical',
      label: {
        position: 'top'
      },
      lineStyle: {
        color: 'source',
        curveness: 0.5
      }
    }
  ]
};
```
