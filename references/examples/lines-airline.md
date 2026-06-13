# 65k+ 飞机航线 / 65k+ Airline

**Category:** `'map, lines'`
**Example dir:** `lines-airline`
**Difficulty:** 

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
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



## Key Points
- This is an official ECharts example from `lines-airline/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
