# lines-airline

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=lines-airline
**Chart Type:** `lines`

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
