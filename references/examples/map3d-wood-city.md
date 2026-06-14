# map3d-wood-city

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=map3d-wood-city
**Chart Type:** `map3D`

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
title: Wood City
category: map3D
titleCN: æ¨è´¨é£æ ¼åå¸
*/
$.getJSON(
  ROOT_PATH + '/data-gl/asset/data/buildings.json',
  function (buildingsGeoJSON) {
    echarts.registerMap('buildings', buildingsGeoJSON);
    var regions = buildingsGeoJSON.features.map(function (feature) {
      return {
        name: feature.properties.name,
        value: Math.max(Math.sqrt(feature.properties.height), 0.1),
        height: Math.max(Math.sqrt(feature.properties.height), 0.1)
      };
    });
    myChart.setOption({
      series: [
        {
          type: 'map3D',
          map: 'buildings',
          shading: 'realistic',
          realisticMaterial: {
            roughness: 0.6,
            textureTiling: 20,
            detailTexture: ROOT_PATH + '/data-gl/asset/woods.jpg'
          },
          postEffect: {
            enable: true,
            bloom: {
              enable: false
            },
            SSAO: {
              enable: true,
              quality: 'medium',
              radius: 10,
              intensity: 1.2
            },
            depthOfField: {
              enable: false,
              focalRange: 5,
              fstop: 1,
              blurRadius: 6
            }
          },
          groundPlane: {
            show: true,
            color: '#333'
          },
          light: {
            main: {
              intensity: 6,
              shadow: true,
              shadowQuality: 'high',
              alpha: 30
            },
            ambient: {
              intensity: 0
            },
            ambientCubemap: {
              texture: ROOT_PATH + '/data-gl/asset/canyon.hdr',
              exposure: 2,
              diffuseIntensity: 1,
              specularIntensity: 1
            }
          },
          viewControl: {
            minBeta: -360,
            maxBeta: 360
          },
          itemStyle: {
            areaColor: '#666'
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
