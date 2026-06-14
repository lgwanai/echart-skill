# sphere-parametric-surface

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sphere-parametric-surface
**Chart Type:** `surface`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

## Reference Code

```javascript
/*
title: Sphere Parametric Surface
category: surface
titleCN: Sphere Parametric Surface
*/
option = {
  tooltip: {},
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
  xAxis3D: {},
  yAxis3D: {},
  zAxis3D: {},
  grid3D: {},
  series: [
    {
      type: 'surface',
      parametric: true,
      // shading: 'albedo',
      parametricEquation: {
        u: {
          min: -Math.PI,
          max: Math.PI,
          step: Math.PI / 20
        },
        v: {
          min: 0,
          max: Math.PI,
          step: Math.PI / 20
        },
        x: function (u, v) {
          return Math.sin(v) * Math.sin(u);
        },
        y: function (u, v) {
          return Math.sin(v) * Math.cos(u);
        },
        z: function (u, v) {
          return Math.cos(v);
        }
      }
    }
  ]
};
```
