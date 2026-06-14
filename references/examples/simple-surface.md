# simple-surface

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=simple-surface
**Chart Type:** `value`

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
title: Simple Surface
category: surface
titleCN: Simple Surface
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
    type: 'value'
  },
  grid3D: {
    viewControl: {
      // projection: 'orthographic'
    }
  },
  series: [
    {
      type: 'surface',
      wireframe: {
        // show: false
      },
      equation: {
        x: {
          step: 0.05
        },
        y: {
          step: 0.05
        },
        z: function (x, y) {
          if (Math.abs(x) < 0.1 && Math.abs(y) < 0.1) {
            return '-';
          }
          return Math.sin(x * Math.PI) * Math.sin(y * Math.PI);
        }
      }
    }
  ]
};
```
