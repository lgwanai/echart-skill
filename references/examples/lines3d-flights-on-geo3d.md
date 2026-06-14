# lines3d-flights-on-geo3d

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=lines3d-flights-on-geo3d
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
title: Flights on Geo3D
category: lines3D
titleCN: Flights on Geo3D
*/
$.getJSON(ROOT_PATH + '/data-gl/asset/data/flights.json', function (data) {
  function getAirportCoord(idx) {
    return [data.airports[idx][3], data.airports[idx][4]];
  }
  var routes = data.routes.map(function (airline) {
    return [getAirportCoord(airline[1]), getAirportCoord(airline[2])];
  });
  myChart.setOption({
    geo3D: {
      map: 'world',
      shading: 'color',
      environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
      silent: true,
      groundPlane: {
        show: false
      },
      light: {
        main: {
          intensity: 0
        },
        ambient: {
          intensity: 0
        }
      },
      viewControl: {
        distance: 50
      },
      itemStyle: {
        color: '#111'
      },
      boxHeight: 0.5
    },
    series: [
      {
        type: 'lines3D',
        coordinateSystem: 'geo3D',
        effect: {
          show: true,
          trailWidth: 2,
          trailLength: 0.2
        },
        blendMode: 'lighter',
        lineStyle: {
          width: 0,
          color: 'rgb(50, 50, 150)',
          opacity: 0.2
        },
        data: routes
      }
    ]
  });
});
window.addEventListener('keydown', function () {
  myChart.dispatchAction({
    type: 'lines3DToggleEffect',
    seriesIndex: 0
  });
});
```
