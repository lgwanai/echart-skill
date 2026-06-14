# map3d-wood-map

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=map3d-wood-map
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
