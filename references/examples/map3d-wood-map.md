# map3d-wood-map

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=map3d-wood-map
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
title: æ¨è´¨ä¸çå°å¾
category: map3D
titleCN: æ¨è´¨ä¸çå°å¾
*/
$.getJSON(ROOT_PATH + '/data-gl/asset/data/alcohol.json', function (data) {
  var regionData = data.map(function (item) {
    return {
      name: item[0],
      height: Math.pow(item[1], 0.2) + 1
    };
  });
  option = {
    series: [
      {
        type: 'map3D',
        map: 'world',
        shading: 'realistic',
        realisticMaterial: {
          roughness: ROOT_PATH + '/data-gl/asset/wood/roughness.jpg',
          normalTexture: ROOT_PATH + '/data-gl/asset/wood/normal.jpg',
          detailTexture: ROOT_PATH + '/data-gl/asset/wood/diffuse.jpg',
          textureTiling: [2, 2]
        },
        postEffect: {
          enable: true,
          SSAO: {
            enable: true,
            radius: 3,
            intensity: 1.4,
            quality: 'high'
          }
        },
        light: {
          main: {
            intensity: 2,
            shadow: true,
            shadowQuality: 'high',
            alpha: 150,
            beta: 0
          },
          ambient: {
            intensity: 0
          },
          ambientCubemap: {
            diffuseIntensity: 2,
            specularIntensity: 2,
            texture: ROOT_PATH + '/data-gl/asset/canyon.hdr'
          }
        },
        viewControl: {
          alpha: 89,
          rotateMouseButton: 'right',
          panMouseButton: 'left',
          distance: 80
        },
        groundPlane: {
          show: true,
          color: '#333',
          realisticMaterial: {
            roughness: ROOT_PATH + '/data-gl/asset/redbricks/roughness.jpg',
            normalTexture: ROOT_PATH + '/data-gl/asset/redbricks/normal.jpg',
            detailTexture: ROOT_PATH + '/data-gl/asset/redbricks/diffuse.jpg',
            textureTiling: [8, 4]
          }
        },
        data: regionData
      }
    ]
  };
  myChart.setOption(option);
});
```
