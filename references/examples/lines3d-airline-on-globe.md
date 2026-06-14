# lines3d-airline-on-globe

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=lines3d-airline-on-globe
**Chart Type:** `lines3D`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `flights.json`:

```json
{
  "airportsFields": [
    "name",
    "city",
    "country",
    "longitude",
    "latitude"
  ],
  "airlineFields": [
    "name",
    "country"
  ],
  "airports": [
    [
      "Goroka",
      "Goroka",
      "Papua New Guinea",
      145.391881,
      -6.081689
    ],
    [
      "Madang",
      "Madang",
      "Papua New Guinea",
      145.7887,
      -5.207083
    ],
    [
      "Mount Hagen",
      "Mount Hagen",
      "Papua New Guinea",
      144.295861,
      -5.826789
    ],
    [
   
...
```

Agent: build DuckDB query to produce matching data structure.
## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Airline on Globe
category: lines3D
titleCN: Airline on Globe
*/
$.getJSON(ROOT_PATH + '/data-gl/asset/data/flights.json', function (data) {
  function getAirportCoord(idx) {
    return [data.airports[idx][3], data.airports[idx][4]];
  }
  var routes = data.routes.map(function (airline) {
    return [getAirportCoord(airline[1]), getAirportCoord(airline[2])];
  });
  myChart.setOption({
    backgroundColor: '#000',
    globe: {
      baseTexture: ROOT_PATH + '/data-gl/asset/world.topo.bathy.200401.jpg',
      heightTexture:
        ROOT_PATH + '/data-gl/asset/bathymetry_bw_composite_4k.jpg',
      shading: 'lambert',
      light: {
        ambient: {
          intensity: 0.4
        },
        main: {
          intensity: 0.4
        }
      },
      viewControl: {
        autoRotate: false
      }
    },
    series: {
      type: 'lines3D',
      coordinateSystem: 'globe',
      blendMode: 'lighter',
      lineStyle: {
        width: 1,
        color: 'rgb(50, 50, 150)',
        opacity: 0.1
      },
      data: routes
    }
  });
});
```
