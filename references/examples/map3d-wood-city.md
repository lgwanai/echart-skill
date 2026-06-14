# map3d-wood-city

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=map3d-wood-city
**Chart Type:** `map3D`

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
