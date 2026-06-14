# 基础和弦图

**Category:** `chord`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=chord-simple
**Template:** examples/chord-simple.html
**Data Format:** `{ nodes: [{name: string}, ...], links: [{source: string, target: string, value: number}, ...] }`
**Features:** labels displayed

## Official Option Code

```javascript
/*
title: Basic Chord
category: chord
titleCN: 基础和弦图
difficulty: 0
since: 6.0.0
*/
option = {
  tooltip: {},
  legend: {},
  series: [
    {
      type: 'chord',
      clockwise: false,
      label: { show: true },
      lineStyle: { color: 'target' },
      data: [{ name: 'A' }, { name: 'B' }, { name: 'C' }, { name: 'D' }],
      links: [
        { source: 'A', target: 'B', value: 40 },
        { source: 'A', target: 'C', value: 20 },
        { source: 'B', target: 'D', value: 20 }
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
- Build: `scripts/build_template.py examples/chord-simple.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
