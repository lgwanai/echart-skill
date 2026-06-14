# geo-seatmap-flight

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=geo-seatmap-flight
**Chart Type:** `unknown`

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
