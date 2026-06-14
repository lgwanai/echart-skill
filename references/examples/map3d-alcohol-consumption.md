# map3d-alcohol-consumption

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=map3d-alcohol-consumption
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
title: Map3D - Alcohol Consumption
category: map3D
titleCN: Map3D - Alcohol Consumption
*/
$.getJSON(ROOT_PATH + '/data-gl/asset/data/alcohol.json', function (data) {
  var regionData = data.map(function (item) {
    return {
      name: item[0],
      value: item[1]
    };
  });
  console.log(regionData);
  myChart.setOption({
    backgroundColor: '#cdcfd5',
    visualMap: {
      min: 0,
      max: 15,
      realtime: true,
      calculable: true,
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
        map: 'world',
        shading: 'lambert',
        realisticMaterial: {
          roughness: 0.2,
          metalness: 0
        },
        postEffect: {
          enable: true,
          SSAO: {
            enable: true,
            radius: 2,
            intensity: 1
          }
        },
        groundPlane: {
          show: true
        },
        light: {
          main: {
            intensity: 2,
            shadow: true,
            shadowQuality: 'high',
            alpha: 30
          },
          ambient: {
            intensity: 0
          },
          ambientCubemap: {
            texture: ROOT_PATH + '/data-gl/asset/canyon.hdr',
            exposure: 1,
            diffuseIntensity: 1
          }
        },
        viewControl: {
          distance: 50
        },
        regionHeight: 1,
        data: regionData
      }
    ]
  });
});
```
