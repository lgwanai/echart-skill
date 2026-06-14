# lines-airline

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=lines-airline
**Chart Type:** `lines`

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
title: 65k+ Airline
category: 'map, lines'
titleCN: 65k+ 飞机航线
*/
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/data/flights.json', function (data) {
  myChart.hideLoading();
  function getAirportCoord(idx) {
    return [data.airports[idx][3], data.airports[idx][4]];
  }
  var routes = data.routes.map(function (airline) {
    return [getAirportCoord(airline[1]), getAirportCoord(airline[2])];
  });
  myChart.setOption(
    (option = {
      title: {
        text: 'World Flights',
        left: 'center',
        textStyle: {
          color: '#eee'
        }
      },
      backgroundColor: '#003',
      tooltip: {
        formatter: function (param) {
          var route = data.routes[param.dataIndex];
          return (
            data.airports[route[1]][1] + ' > ' + data.airports[route[2]][1]
          );
        }
      },
      geo: {
        map: 'world',
        left: 0,
        right: 0,
        silent: true,
        roam: true,
        itemStyle: {
          borderColor: '#003',
          color: '#005'
        }
      },
      series: [
        {
          type: 'lines',
          coordinateSystem: 'geo',
          data: routes,
          large: true,
          largeThreshold: 100,
          lineStyle: {
            opacity: 0.05,
            width: 0.5,
            curveness: 0.3
          },
          blendMode: 'lighter'
        }
      ]
    })
  );
});
```
