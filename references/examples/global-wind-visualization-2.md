# global-wind-visualization-2

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=global-wind-visualization-2
**Chart Type:** `flowGL`

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
title: Global Wind Visualization 2
category: flowGL
tags: bmap
titleCN: Global Wind Visualization 2
videoStart: 2000
videoEnd: 10000
*/
$.getJSON(ROOT_PATH + '/data-gl/asset/data/gfs.json', function (windData) {
  buildGrid(windData, function (header, grid) {
    var data = [];
    var p = 0;
    var maxMag = 0;
    var minMag = Infinity;
    for (var j = 0; j < header.ny; j++) {
      for (var i = 0; i < header.nx; i++) {
        var vx = grid[j][i][0];
        var vy = grid[j][i][1];
        var mag = Math.sqrt(vx * vx + vy * vy);
        var lng = (i / header.nx) * 360;
        if (lng >= 180) {
          lng = 180 - lng;
        }
        // æ°æ®æ¯ä¸ä¸ªä¸ç»´æ°ç»
        // [ [ç»åº¦, ç»´åº¦ï¼åéç»åº¦æ¹åçå¼ï¼åéç»´åº¦æ¹åçå¼] ]
        data.push([lng, 90 - (j / header.ny) * 180, vx, vy, mag]);
        maxMag = Math.max(mag, maxMag);
        minMag = Math.min(mag, minMag);
      }
    }
    myChart.setOption({
      backgroundColor: '#001122',
      visualMap: {
        left: 'right',
        min: minMag,
        max: maxMag,
        dimension: 4,
        inRange: {
          // color: ['green', 'yellow', 'red']
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
        realtime: false,
        calculable: true,
        textStyle: {
          color: '#fff'
        }
      },
      bmap: {
        center: [0, 0],
        zoom: 1,
        roam: true,
        mapStyle: {
          styleJson: [
            {
              featureType: 'water',
              elementType: 'all',
              stylers: {
                color: '#031628'
              }
            },
            {
              featureType: 'land',
              elementType: 'geometry',
              stylers: {
                color: '#000102'
              }
            },
            {
              featureType: 'highway',
              elementType: 'all',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'arterial',
              elementType: 'geometry.fill',
              stylers: {
                color: '#000000'
              }
            },
            {
              featureType: 'arterial',
              elementType: 'geometry.stroke',
              stylers: {
                color: '#0b3d51'
              }
            },
            {
              featureType: 'local',
              elementType: 'geometry',
              stylers: {
                color: '#000000'
              }
            },
            {
              featureType: 'railway',
              elementType: 'geometry.fill',
              stylers: {
                color: '#000000'
              }
            },
            {
              featureType: 'railway',
              elementType: 'geometry.stroke',
              stylers: {
                color: '#08304b'
              }
            },
            {
              featureType: 'subway',
              elementType: 'geometry',
              stylers: {
                lightness: -70
              }
            },
            {
              featureType: 'building',
              elementType: 'geometry.fill',
              stylers: {
                color: '#000000'
              }
            },
            {
              featureType: 'all',
              elementType: 'labels.text.fill',
              stylers: {
                color: '#857f7f'
              }
            },
            {
              featureType: 'all',
              elementType: 'labels.text.stroke',
              stylers: {
                color: '#000000'
              }
            },
            {
              featureType: 'building',
              elementType: 'geometry',
              stylers: {
                color: '#022338'
              }
            },
            {
              featureType: 'green',
              elementType: 'geometry',
              stylers: {
                color: '#062032'
              }
            },
            {
              featureType: 'boundary',
              elementType: 'all',
              stylers: {
                color: '#465b6c'
              }
            },
            {
              featureType: 'manmade',
              elementType: 'all',
              stylers: {
                color: '#022338'
              }
            },
            {
              featureType: 'label',
              elementType: 'all',
              stylers: {
                visibility: 'off'
              }
            }
          ]
        }
      },
      series: [
        {
          type: 'flowGL',
          coordinateSystem: 'bmap',
          data: data,
          supersampling: 4,
          particleType: 'line',
          particleDensity: 128,
          particleSpeed: 1,
          // gridWidth: windData.nx,
          // gridHeight: windData.ny,
          itemStyle: {
            opacity: 0.7
          }
        }
      ]
    });
  });
});
// https://github.com/Esri/wind-js/blob/master/windy.js#L41
var createWindBuilder = function (uComp, vComp) {
  var uData = uComp.data,
    vData = vComp.data;
  return {
    header: uComp.header,
    //recipe: recipeFor("wind-" + uComp.header.surface1Value),
    data: function (i) {
      return [uData[i], vData[i]];
    }
  };
};
var createBuilder = function (data) {
  var uComp = null,
    vComp = null,
    scalar = null;
  data.forEach(function (record) {
    switch (
      record.header.parameterCategory +
      ',' +
      record.header.parameterNumber
    ) {
      case '2,2':
        uComp = record;
        break;
      case '2,3':
        vComp = record;
        break;
      default:
        scalar = record;
    }
  });
  return createWindBuilder(uComp, vComp);
};
var buildGrid = function (data, callback) {
  var builder = createBuilder(data);
  var header = builder.header;
  var Î»0 = header.lo1,
    Ï0 = header.la1; // the grid's origin (e.g., 0.0E, 90.0N)
  var ÎÎ» = header.dx,
    ÎÏ = header.dy; // distance between grid points (e.g., 2.5 deg lon, 2.5 deg lat)
  var ni = header.nx,
    nj = header.ny; // number of grid points W-E and N-S (e.g., 144 x 73)
  var date = new Date(header.refTime);
  date.setHours(date.getHours() + header.forecastTime);
  // Scan mode 0 assumed. Longitude increases from Î»0, and latitude decreases from Ï0.
  // http://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_table3-4.shtml
  var grid = [],
    p = 0;
  var isContinuous = Math.floor(ni * ÎÎ») >= 360;
  for (var j = 0; j < nj; j++) {
    var row = [];
    for (var i = 0; i < ni; i++, p++) {
      row[i] = builder.data(p);
    }
    if (isContinuous) {
      // For wrapped grids, duplicate first column as last column to simplify interpolation logic
      row.push(row[0]);
    }
    grid[j] = row;
  }
  callback(header, grid);
};
```
