# surface-wave

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=surface-wave

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Surface Wave
category: surface
titleCN: Surface Wave
*/
option = {
  tooltip: {},
  backgroundColor: '#fff',
  visualMap: {
    show: false,
    dimension: 2,
    min: -1,
    max: 1,
    inRange: {
      color: [
        '#313695',
        '#4575b4',
        '#74add1',
        '#abd9e9',
        '#e0f3f8',
        '#ffffbf',
        '#fee090',
        '#fdae61',
        '#f46d43',
        '#d73027',
        '#a50026'
      ]
    }
  },
  xAxis3D: {
    type: 'value'
  },
  yAxis3D: {
    type: 'value'
  },
  zAxis3D: {
    type: 'value',
    max: 1,
    splitNumber: 2
  },
  grid3D: {
    viewControl: {
      // projection: 'orthographic'
    },
    boxHeight: 40
  },
  series: [
    {
      type: 'surface',
      wireframe: {
        show: false
      },
      shading: 'color',
      equation: {
        x: {
          step: 0.05,
          min: -3,
          max: 3
        },
        y: {
          step: 0.05,
          min: -3,
          max: 3
        },
        z: function (x, y) {
          return (Math.sin(x * x + y * y) * x) / 3.14;
        }
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
