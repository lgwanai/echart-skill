# polar-endAngle

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=polar-endAngle

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

**4 data arrays** to replace:
- `data[0]`: `data: ['S1', 'S2', 'S3']`
- `data[1]`: `data: ['T1', 'T2', 'T3']`
- `data[2]`: `data: [1, 2, 3]`
- `data[3]`: `data: [1, 2, 3]`

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Polar endAngle
category: bar
titleCN: 极坐标系 endAngle
difficulty: 2
*/
option = {
  tooltip: {},
  angleAxis: [
    {
      type: 'category',
      polarIndex: 0,
      startAngle: 90,
      endAngle: 0,
      data: ['S1', 'S2', 'S3']
    },
    {
      type: 'category',
      polarIndex: 1,
      startAngle: -90,
      endAngle: -180,
      data: ['T1', 'T2', 'T3']
    }
  ],
  radiusAxis: [{ polarIndex: 0 }, { polarIndex: 1 }],
  polar: [{}, {}],
  series: [
    {
      type: 'bar',
      polarIndex: 0,
      data: [1, 2, 3],
      coordinateSystem: 'polar'
    },
    {
      type: 'bar',
      polarIndex: 1,
      data: [1, 2, 3],
      coordinateSystem: 'polar'
    }
  ]
};
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
