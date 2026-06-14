# 基础矩形树图

**Category:** `treemap`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=treemap-simple
**Template:** examples/treemap-simple.html
**Data Format:** `[{name: string, value?: number, children?: [...]}, ...]`

## Official Option Code

```javascript
/*
title: Basic Treemap
category: treemap
titleCN: 基础矩形树图
*/
option = {
  series: [
    {
      type: 'treemap',
      data: [
        {
          name: 'nodeA',
          value: 10,
          children: [
            {
              name: 'nodeAa',
              value: 4
            },
            {
              name: 'nodeAb',
              value: 6
            }
          ]
        },
        {
          name: 'nodeB',
          value: 20,
          children: [
            {
              name: 'nodeBa',
              value: 20,
              children: [
                {
                  name: 'nodeBa1',
                  value: 20
                }
              ]
            }
          ]
        }
      ]
    }
  ]
};
```

## Placeholders

| Placeholder | Type | Description |
|-------------|------|-------------|
| `{{{TITLE}}}` | string | title |

## Usage
- Build: `scripts/build_template.py examples/treemap-simple.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
