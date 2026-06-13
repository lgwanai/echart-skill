# Surface Wave

**Category:** `surface`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=surface-wave
**Template:** NONE — use knowledge base
**Data Format:** `N/A`
**Features:** visualMap component required

## Official Option Code

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

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
