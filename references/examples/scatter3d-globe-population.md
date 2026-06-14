# scatter3d-globe-population

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter3d-globe-population
**Chart Type:** `scatter3D`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `population.json`:

```json
[
  [
    -83,
    76.5,
    1.1
  ],
  [
    -85.5,
    73.5,
    2.9
  ],
  [
    -78,
    73,
    1.5
  ]
]
```

Agent: build DuckDB query to produce matching data structure.
## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Scatter3D - Global Population
category: scatter3D
titleCN: ä¸ç»´æ£ç¹å¾ - å¨çäººå£åå¸
*/
$.getJSON(ROOT_PATH + '/data-gl/asset/data/population.json', function (data) {
  data = data
    .filter(function (dataItem) {
      return dataItem[2] > 0;
    })
    .map(function (dataItem) {
      return [dataItem[0], dataItem[1], Math.sqrt(dataItem[2])];
    });
  myChart.setOption({
    visualMap: {
      show: false,
      min: 0,
      max: 60,
      inRange: {
        symbolSize: [1.0, 10.0]
      }
    },
    globe: {
      environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
      heightTexture:
        ROOT_PATH + '/data-gl/asset/bathymetry_bw_composite_4k.jpg',
      displacementScale: 0.05,
      displacementQuality: 'high',
      globeOuterRadius: 100,
      baseColor: '#000',
      shading: 'realistic',
      realisticMaterial: {
        roughness: 0.2,
        metalness: 0
      },
      postEffect: {
        enable: true,
        depthOfField: {
          focalRange: 15,
          enable: true,
          focalDistance: 100
        }
      },
      temporalSuperSampling: {
        enable: true
      },
      light: {
        ambient: {
          intensity: 0
        },
        main: {
          intensity: 0.1,
          shadow: false
        },
        ambientCubemap: {
          texture: ROOT_PATH + '/data-gl/asset/lake.hdr',
          exposure: 1,
          diffuseIntensity: 0.5,
          specularIntensity: 2
        }
      },
      viewControl: {
        autoRotate: false,
        beta: 180,
        alpha: 20,
        distance: 100
      }
    },
    series: {
      type: 'scatter3D',
      coordinateSystem: 'globe',
      blendMode: 'lighter',
      symbolSize: 2,
      itemStyle: {
        color: 'rgb(50, 50, 150)',
        opacity: 1
      },
      data: data
    }
  });
});
```
