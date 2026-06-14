# custom-hexbin

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=custom-hexbin
**Chart Type:** `group`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **2 data array(s)** to replace:

### data[0]: `legend`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['bar', 'error']`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `unknown`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [0]`
- **Replace with**: real data from DuckDB in the same format


## External Data Format

This example uses external data. Format from `kawhi-leonard-16-17-regular.json`:

```json
[
  [
    "Shot Chart Detail",
    "0021600003",
    "13",
    "202695",
    "Kawhi Leonard",
    "1610612759",
    "San Antonio Spurs",
    "1",
    "9",
    "41",
    "Missed Shot",
    "Jump Shot",
    "3PT Field Goal",
    "Above the Break 3",
    "Center(C)",
    "24+ ft.",
    24,
    -5.5,
    29.15,
    1,
    "missed",
    "20161025",
    "GSW",
    "SAS",
    0,
    3
  ],
  [
    "Shot Chart Detail",
    "0021600003",
    "27",
    "202695",
    "Kawhi Leonard",
    "1610612759",
    
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
title: Hexagonal Binning
category: custom, map
titleCN: 六边形分箱图（自定义系列）
difficulty: 6
*/
// Hexbin statistics code based on [d3-hexbin](https://github.com/d3/d3-hexbin)
function hexBinStatistics(points, r) {
  var dx = r * 2 * Math.sin(Math.PI / 3);
  var dy = r * 1.5;
  var binsById = {};
  var bins = [];
  for (var i = 0, n = points.length; i < n; ++i) {
    var point = points[i];
    var px = point[0];
    var py = point[1];
    if (isNaN(px) || isNaN(py)) {
      continue;
    }
    var pj = Math.round((py = py / dy));
    var pi = Math.round((px = px / dx - (pj & 1) / 2));
    var py1 = py - pj;
    if (Math.abs(py1) * 3 > 1) {
      var px1 = px - pi;
      var pi2 = pi + (px < pi ? -1 : 1) / 2;
      var pj2 = pj + (py < pj ? -1 : 1);
      var px2 = px - pi2;
      var py2 = py - pj2;
      if (px1 * px1 + py1 * py1 > px2 * px2 + py2 * py2) {
        pi = pi2 + (pj & 1 ? 1 : -1) / 2;
        pj = pj2;
      }
    }
    var id = pi + '-' + pj;
    var bin = binsById[id];
    if (bin) {
      bin.points.push(point);
    } else {
      bins.push((bin = binsById[id] = { points: [point] }));
      bin.x = (pi + (pj & 1) / 2) * dx;
      bin.y = pj * dy;
    }
  }
  var maxBinLen = -Infinity;
  for (var i = 0; i < bins.length; i++) {
    maxBinLen = Math.max(maxBinLen, bins.length);
  }
  return {
    maxBinLen: maxBinLen,
    bins: bins
  };
}
$.when(
  $.getJSON(ROOT_PATH + '/data/asset/data/kawhi-leonard-16-17-regular.json'),
  $.getJSON(ROOT_PATH + '/data/asset/data/nba-court.json')
).done(function (shotData, nbaCourt) {
  shotData = shotData[0];
  nbaCourt = nbaCourt[0];
  echarts.registerMap('nbaCourt', nbaCourt.borderGeoJSON);
  var backgroundColor = '#333';
  var hexagonRadiusInGeo = 1;
  var hexBinResult = hexBinStatistics(
    shotData.data.map(function (item) {
      // "shot_made_flag" made missed
      var made = item[shotData.schema.indexOf('shot_made_flag')];
      return [
        item[shotData.schema.indexOf('loc_x')],
        item[shotData.schema.indexOf('loc_y')],
        made === 'made' ? 1 : 0
      ];
    }),
    hexagonRadiusInGeo
  );
  var data = hexBinResult.bins.map(function (bin) {
    var made = 0;
    bin.points.forEach(function (point) {
      made += point[2];
    });
    return [
      bin.x,
      bin.y,
      bin.points.length,
      ((made / bin.points.length) * 100).toFixed(2)
    ];
  });
  function renderItemHexBin(params, api) {
    var center = api.coord([api.value(0), api.value(1)]);
    var points = [];
    var pointsBG = [];
    var maxViewRadius = api.size([hexagonRadiusInGeo, 0])[0];
    var minViewRadius = Math.min(maxViewRadius, 4);
    var extentMax = Math.log(Math.sqrt(hexBinResult.maxBinLen));
    var viewRadius = echarts.number.linearMap(
      Math.log(Math.sqrt(api.value(2))),
      [0, extentMax],
      [minViewRadius, maxViewRadius]
    );
    var angle = Math.PI / 6;
    for (var i = 0; i < 6; i++, angle += Math.PI / 3) {
      points.push([
        center[0] + viewRadius * Math.cos(angle),
        center[1] + viewRadius * Math.sin(angle)
      ]);
      pointsBG.push([
        center[0] + maxViewRadius * Math.cos(angle),
        center[1] + maxViewRadius * Math.sin(angle)
      ]);
    }
    return {
      type: 'group',
      children: [
        {
          type: 'polygon',
          shape: {
            points: points
          },
          style: {
            stroke: '#ccc',
            fill: api.visual('color'),
            lineWidth: 1
          }
        },
        {
          type: 'polygon',
          shape: {
            points: pointsBG
          },
          style: {
            stroke: null,
            fill: 'rgba(0,0,0,0.5)',
            lineWidth: 0
          },
          z2: -19
        }
      ]
    };
  }
  function renderItemNBACourt(param, api) {
    return {
      type: 'group',
      children: nbaCourt.geometry.map(function (item) {
        return {
          type: item.type,
          style: {
            stroke: '#aaa',
            fill: null,
            lineWidth: 1.5
          },
          shape: {
            points: item.points.map(api.coord)
          }
        };
      })
    };
  }
  option = {
    backgroundColor: backgroundColor,
    tooltip: {
      backgroundColor: 'rgba(255,255,255,0.9)',
      textStyle: {
        color: '#333'
      }
    },
    animation: false,
    title: {
      text: 'Some Player',
      subtext: 'Regular Season',
      backgroundColor: backgroundColor,
      top: 10,
      left: 10,
      textStyle: {
        color: '#eee'
      }
    },
    legend: {
      data: ['bar', 'error']
    },
    geo: {
      left: 0,
      right: 0,
      top: 0,
      bottom: 0,
      roam: true,
      silent: true,
      itemStyle: {
        color: backgroundColor,
        borderWidth: 0
      },
      map: 'nbaCourt'
    },
    visualMap: {
      type: 'continuous',
      orient: 'horizontal',
      right: 30,
      top: 40,
      min: 0,
      max: 100,
      align: 'bottom',
      text: [null, 'FG:   '],
      dimension: 3,
      calculable: true,
      textStyle: {
        color: '#eee'
      },
      formatter: '{value} %',
      inRange: {
        // color: ['rgba(241,222,158, 0.3)', 'rgba(241,222,158, 1)']
        color: ['green', 'yellow']
      }
    },
    series: [
      {
        type: 'custom',
        coordinateSystem: 'geo',
        geoIndex: 0,
        renderItem: renderItemHexBin,
        dimensions: [
          null,
          null,
          'Field Goals Attempted (hexagon size)',
          'Field Goal Percentage (color)'
        ],
        encode: {
          tooltip: [2, 3]
        },
        data: data
      },
      {
        coordinateSystem: 'geo',
        type: 'custom',
        geoIndex: 0,
        renderItem: renderItemNBACourt,
        silent: true,
        data: [0]
      }
    ]
  };
  myChart.setOption(option);
});
```
