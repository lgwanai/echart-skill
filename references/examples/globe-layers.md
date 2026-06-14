# globe-layers

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=globe-layers
**Chart Type:** `blend`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Globe Layers
category: globe
titleCN: å°çå¾å±
difficulty: 1
videoStart: 2000
videoEnd: 6000
*/
option = {
  backgroundColor: '#000',
  globe: {
    baseTexture: ROOT_PATH + '/data-gl/asset/earth.jpg',
    heightTexture: ROOT_PATH + '/data-gl/asset/bathymetry_bw_composite_4k.jpg',
    displacementScale: 0.1,
    shading: 'lambert',
    environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
    light: {
      ambient: {
        intensity: 0.1
      },
      main: {
        intensity: 1.5
      }
    },
    layers: [
      {
        type: 'blend',
        blendTo: 'emission',
        texture: ROOT_PATH + '/data-gl/asset/night.jpg'
      },
      {
        type: 'overlay',
        texture: ROOT_PATH + '/data-gl/asset/clouds.png',
        shading: 'lambert',
        distance: 5
      }
    ]
  },
  series: []
};
```
