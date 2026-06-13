# 垂直方向的桑基图

**Category:** `sankey`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sankey-vertical
**Template:** sankey/basic.html
**Data Format:** `{ nodes: [{name: string, itemStyle?: {}}, ...], links: [{source: string, target: string, value: number}, ...] }`
**Features:** emphasis/hover effects

## Official Option Code

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

## Usage
- Build: `scripts/build_template.py sankey/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
