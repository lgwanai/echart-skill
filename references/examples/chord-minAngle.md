# 和弦图 minAngle

**Category:** `chord`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=chord-minAngle
**Template:** chord/basic.html
**Data Format:** `{ nodes: [{name: string}, ...], links: [{source: string, target: string, value: number}, ...] }`
**Features:** labels displayed

## Official Option Code

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

## Usage
- Build: `scripts/build_template.py chord/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
