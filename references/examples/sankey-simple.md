# 基础桑基图 / Basic Sankey

**Category:** `sankey`
**Example dir:** `sankey-simple`
**Difficulty:** 0

## Template Match
- **sankey/basic.html** — Sankey

## Option Code
```javascript
option = {
  series: {
    type: 'sankey',
    layout: 'none',
    emphasis: {
      focus: 'adjacency'
    },
    data: [
      {
        name: 'a'
      },
      {
        name: 'b'
      },
      {
        name: 'a1'
      },
      {
        name: 'a2'
      },
      {
        name: 'b1'
      },
      {
        name: 'c'
      }
    ],
    links: [
      {
        source: 'a',
        target: 'a1',
        value: 5
      },
      {
        source: 'a',
        target: 'a2',
        value: 3
      },
      {
        source: 'b',
        target: 'b1',
        value: 8
      },
      {
        source: 'a',
        target: 'b1',
        value: 3
      },
      {
        source: 'b1',
        target: 'a1',
        value: 1
      },
      {
        source: 'b1',
        target: 'c',
        value: 2
      }
    ]
  }
};
```



## Key Points
- This is an official ECharts example from `sankey-simple/main.js`
- Template data format: `{ nodes: [{name: string, itemStyle?: {}}, ...], links: [{source: string, target: string, value: number}, ...] }`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
