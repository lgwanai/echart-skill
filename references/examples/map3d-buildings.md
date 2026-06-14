# map3d-buildings

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=map3d-buildings
**Chart Type:** `map3D`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `buildings.json`:

```json
{
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "0",
        "height": 0.7
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          "@@Ӽѻ࡮ϐ˥ɾ؝ʳmpȓǮʣĻ"
        ],
        "encodeOffsets": [
          [
            13368440,
            52534490
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "name": "1",
        "height": 0
      },
      "geometry": {
        "type": "Polygo
...
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
title: Buildings
category: map3D
titleCN: ä¸ç»´å»ºç­
*/
$.getJSON(
  ROOT_PATH + '/data-gl/asset/data/buildings.json',
  function (buildingsGeoJSON) {
    echarts.registerMap('buildings', buildingsGeoJSON);
    var regions = buildingsGeoJSON.features.map(function (feature) {
      return {
        name: feature.properties.name,
        value: Math.random(),
        height: feature.properties.height / 10
      };
    });
    myChart.setOption({
      visualMap: {
        show: false,
        min: 0.4,
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
      series: [
        {
          type: 'map3D',
          map: 'buildings',
          shading: 'realistic',
          environment: '#000',
          realisticMaterial: {
            roughness: 0.6,
            textureTiling: 20
          },
          postEffect: {
            enable: true,
            SSAO: {
              enable: true,
              intensity: 1.3,
              radius: 5
            },
            screenSpaceReflection: {
              enable: false
            },
            depthOfField: {
              enable: true,
              blurRadius: 4,
              focalDistance: 30
            }
          },
          light: {
            main: {
              intensity: 3,
              alpha: 40,
              shadow: true,
              shadowQuality: 'high'
            },
            ambient: {
              intensity: 0
            },
            ambientCubemap: {
              texture: ROOT_PATH + '/data-gl/asset/pisa.hdr',
              exposure: 1,
              diffuseIntensity: 0.5,
              specularIntensity: 1
            }
          },
          groundPlane: {
            show: false,
            color: '#333'
          },
          viewControl: {
            minBeta: -360,
            maxBeta: 360,
            alpha: 50,
            center: [50, 0, -10],
            distance: 30,
            minDistance: 5,
            panMouseButton: 'left',
            rotateMouseButton: 'middle',
            zoomSensitivity: 0.5
          },
          itemStyle: {
            areaColor: '#666'
            // borderColor: '#222',
            // borderWidth: 1
          },
          label: {
            color: 'white'
          },
          silent: true,
          instancing: true,
          boxWidth: 200,
          boxHeight: 1,
          data: regions
        }
      ]
    });
  }
);
```
