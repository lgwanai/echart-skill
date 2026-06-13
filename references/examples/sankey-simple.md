# 基础桑基图

**Category:** `sankey`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sankey-simple
**Template:** examples/sankey-simple.html
**Data Format:** `{ nodes: [{name: string, itemStyle?: {}}, ...], links: [{source: string, target: string, value: number}, ...] }`
**Features:** emphasis/hover effects

## Official Option Code

```javascript
/*
title: Basic Sankey
category: sankey
titleCN: 基础桑基图
difficulty: 0
*/
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

## Usage
- Build: `scripts/build_template.py examples/sankey-simple.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
