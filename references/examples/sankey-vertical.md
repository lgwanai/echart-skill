# 垂直方向的桑基图 / Sankey Orient Vertical

**Category:** `sankey`
**Example dir:** `sankey-vertical`
**Difficulty:** 1

## Template Match
- **sankey/basic.html** — Sankey

## Option Code
```javascript
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



## Key Points
- This is an official ECharts example from `sankey-vertical/main.js`
- Template data format: `{ nodes: [{name: string, itemStyle?: {}}, ...], links: [{source: string, target: string, value: number}, ...] }`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
