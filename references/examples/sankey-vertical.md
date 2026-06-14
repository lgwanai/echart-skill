# sankey-vertical

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sankey-vertical

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

**1 data arrays** to replace:
- `data[0]`: `data: [
        { name: 'a' },
        { name: 'b' },
        { name: 'a1' },
  ...`

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

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

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
