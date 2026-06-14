# map3d-buildings

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=map3d-buildings
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
