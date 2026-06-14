# geo-seatmap-flight

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=geo-seatmap-flight
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
title: Flight Seatmap with SVG
category: map
titleCN: 航班选座（SVG）
*/
$.get(ROOT_PATH + '/data/asset/geo/flight-seats.svg', function (svg) {
  echarts.registerMap('flight-seats', { svg: svg });
  const takenSeatNames = ['26E', '26D', '26C', '25D', '23C', '21A', '20F'];
  option = {
    tooltip: {},
    geo: {
      map: 'flight-seats',
      roam: true,
      selectedMode: 'multiple',
      layoutCenter: ['50%', '50%'],
      layoutSize: '95%',
      tooltip: {
        show: true
      },
      itemStyle: {
        color: '#fff'
      },
      emphasis: {
        itemStyle: {
          color: undefined,
          borderColor: 'green',
          borderWidth: 2
        },
        label: {
          show: false
        }
      },
      select: {
        itemStyle: {
          color: 'green'
        },
        label: {
          show: false,
          textBorderColor: '#fff',
          textBorderWidth: 2
        }
      },
      regions: makeTakenRegions(takenSeatNames)
    }
  };
  function makeTakenRegions(takenSeatNames) {
    var regions = [];
    for (var i = 0; i < takenSeatNames.length; i++) {
      regions.push({
        name: takenSeatNames[i],
        silent: true,
        itemStyle: {
          color: '#bf0e08'
        },
        emphasis: {
          itemStyle: {
            borderColor: '#aaa',
            borderWidth: 1
          }
        },
        select: {
          itemStyle: {
            color: '#bf0e08'
          }
        }
      });
    }
    return regions;
  }
  myChart.setOption(option);
  // Get selected seats.
  myChart.on('geoselectchanged', function (params) {
    const selectedNames = params.allSelected[0].name.slice();
    // Remove taken seats.
    for (var i = selectedNames.length - 1; i >= 0; i--) {
      if (takenSeatNames.indexOf(selectedNames[i]) >= 0) {
        selectedNames.splice(i, 1);
      }
    }
    console.log('selected', selectedNames);
  });
});
```
