# lines3d-flights-gl

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=lines3d-flights-gl
**Chart Type:** `lines3D`

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
title: Flights GL
category: lines3D
titleCN: Flights GL
videoStart: 2000
videoEnd: 8000
*/
var uploadedDataURL = ROOT_PATH + '/data-gl/asset/data/flights.json';
myChart.showLoading();
$.getJSON(uploadedDataURL, function (data) {
  myChart.hideLoading();
  function getAirportCoord(idx) {
    return [data.airports[idx][3], data.airports[idx][4]];
  }
  var routes = data.routes.map(function (airline) {
    return [getAirportCoord(airline[1]), getAirportCoord(airline[2])];
  });
  myChart.setOption({
    geo3D: {
      map: 'world',
      shading: 'realistic',
      silent: true,
      environment: '#333',
      realisticMaterial: {
        roughness: 0.8,
        metalness: 0
      },
      postEffect: {
        enable: true
      },
      groundPlane: {
        show: false
      },
      light: {
        main: {
          intensity: 1,
          alpha: 30
        },
        ambient: {
          intensity: 0
        }
      },
      viewControl: {
        distance: 70,
        alpha: 89,
        panMouseButton: 'left',
        rotateMouseButton: 'right'
      },
      itemStyle: {
        color: '#000'
      },
      regionHeight: 0.5
    },
    series: [
      {
        type: 'lines3D',
        coordinateSystem: 'geo3D',
        effect: {
          show: true,
          trailWidth: 1,
          trailOpacity: 0.5,
          trailLength: 0.2,
          constantSpeed: 5
        },
        blendMode: 'lighter',
        lineStyle: {
          width: 0.2,
          opacity: 0.05
        },
        data: routes
      }
    ]
  });
  window.addEventListener('keydown', function () {
    myChart.dispatchAction({
      type: 'lines3DToggleEffect',
      seriesIndex: 0
    });
  });
});
```
