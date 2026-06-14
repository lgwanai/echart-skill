# geo3d-with-different-height

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=geo3d-with-different-height
**Chart Type:** `unknown`

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
title: Geo3D with Different Height
category: geo3D
titleCN: Geo3D with Different Height
*/
$.getJSON(
  ROOT_PATH + '/data-gl/asset/data/world-population.json',
  function (populationData) {
    var max = -Infinity;
    var min = Infinity;
    populationData.forEach(function (item) {
      max = Math.max(Math.log(item.value), max);
      min = Math.min(Math.log(item.value), min);
    });
    var regions = populationData.map(function (item) {
      return {
        name: item.name,
        height: ((Math.log(item.value) - min) / (max - min)) * 3
      };
    });
    myChart.setOption(
      (option = {
        backgroundColor: '#cdcfd5',
        geo3D: {
          map: 'world',
          shading: 'lambert',
          lambertMaterial: {
            detailTexture: ROOT_PATH + '/data-gl/asset/woods.jpg',
            textureTiling: 20
          },
          postEffect: {
            enable: true,
            SSAO: {
              enable: true,
              radius: 3,
              quality: 'high'
            }
          },
          groundPlane: {
            show: true
          },
          light: {
            main: {
              intensity: 1,
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
              diffuseIntensity: 0.3
            }
          },
          viewControl: {
            distance: 50
          },
          regionHeight: 0.5,
          regions: regions
        }
      })
    );
  }
);
```
