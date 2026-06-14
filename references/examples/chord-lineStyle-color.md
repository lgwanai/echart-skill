# chord-lineStyle-color

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=chord-lineStyle-color

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

**1 data arrays** to replace:
- `data[0]`: `data: [{ name: 'A' }, { name: 'B' }, { name: 'C' }, { name: 'D' }]`

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Chord lineStyle.color
category: chord
titleCN: 和弦图边的颜色
difficulty: 3
since: 6.0.0
*/
function generateSeries(id, lineColor) {
  return {
    type: 'chord',
    label: { show: true },
    center: [((id * 2 + 1) / 6) * 100 + '%', '50%'],
    radius: ['28%', '32%'],
    lineStyle: {
      color: lineColor
    },
    data: [{ name: 'A' }, { name: 'B' }, { name: 'C' }, { name: 'D' }],
    links: [
      { source: 'A', target: 'B', value: 30 },
      { source: 'A', target: 'C', value: 20 },
      { source: 'B', target: 'D', value: 10 },
      { source: 'C', target: 'A', value: 15 },
      { source: 'D', target: 'A', value: 25 }
    ]
  };
}
function generateTitle(id, text) {
  return {
    text,
    left: ((id * 2 + 1) / 6) * 100 + '%',
    top: '25%',
    textAlign: 'center',
    padding: 0
  };
}
option = {
  tooltip: {},
  legend: {},
  series: [
    generateSeries(0, 'source'),
    generateSeries(1, 'target'),
    generateSeries(2, 'gradient')
  ],
  title: [
    {
      text: 'lineStyle.color',
      textStyle: {
        fontSize: 24
      }
    },
    generateTitle(0, 'source'),
    generateTitle(1, 'target'),
    generateTitle(2, 'gradient')
  ]
};
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
