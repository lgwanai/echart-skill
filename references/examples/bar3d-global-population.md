# bar3d-global-population

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar3d-global-population
**Chart Type:** `bar3D`

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
title: Bar3D - Global Population
category: bar3D
titleCN: Bar3D - å¨çäººå£åå¸
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
    backgroundColor: '#cdcfd5',
    geo3D: {
      map: 'world',
      shading: 'lambert',
      light: {
        main: {
          intensity: 5,
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
          diffuseIntensity: 0.5
        }
      },
      viewControl: {
        distance: 50,
        panMouseButton: 'left',
        rotateMouseButton: 'right'
      },
      groundPlane: {
        show: true,
        color: '#999'
      },
      postEffect: {
        enable: true,
        bloom: {
          enable: false
        },
        SSAO: {
          radius: 1,
          intensity: 1,
          enable: true
        },
        depthOfField: {
          enable: false,
          focalRange: 10,
          blurRadius: 10,
          fstop: 1
        }
      },
      temporalSuperSampling: {
        enable: true
      },
      itemStyle: {},
      regionHeight: 2
    },
    visualMap: {
      max: 40,
      calculable: true,
      realtime: false,
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
      },
      outOfRange: {
        colorAlpha: 0
      }
    },
    series: [
      {
        type: 'bar3D',
        coordinateSystem: 'geo3D',
        shading: 'lambert',
        data: data,
        barSize: 0.1,
        minHeight: 0.2,
        silent: true,
        itemStyle: {
          color: 'orange'
          // opacity: 0.8
        }
      }
    ]
  });
});
```
