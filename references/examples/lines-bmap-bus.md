# lines-bmap-bus

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=lines-bmap-bus
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
title: Bus Lines of Beijing - Baidu Map
category: 'map, lines'
noExplore: true
tags: bmap
titleCN: 北京公交路线 - 百度地图
*/
$.get(ROOT_PATH + '/data/asset/data/lines-bus.json', function (data) {
  let busLines = [].concat.apply(
    [],
    data.map(function (busLine, idx) {
      let prevPt = [];
      let points = [];
      for (let i = 0; i < busLine.length; i += 2) {
        let pt = [busLine[i], busLine[i + 1]];
        if (i > 0) {
          pt = [prevPt[0] + pt[0], prevPt[1] + pt[1]];
        }
        prevPt = pt;
        points.push([pt[0] / 1e4, pt[1] / 1e4]);
      }
      return {
        coords: points
      };
    })
  );
  myChart.setOption(
    (option = {
      backgroundColor: 'transparent',
      bmap: {
        center: [116.46, 39.92],
        zoom: 10,
        roam: true,
        mapStyle: {
          styleJson: [
            {
              featureType: 'water',
              elementType: 'all',
              stylers: {
                color: '#d1d1d1'
              }
            },
            {
              featureType: 'land',
              elementType: 'all',
              stylers: {
                color: '#f3f3f3'
              }
            },
            {
              featureType: 'railway',
              elementType: 'all',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'highway',
              elementType: 'all',
              stylers: {
                color: '#fdfdfd'
              }
            },
            {
              featureType: 'highway',
              elementType: 'labels',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'arterial',
              elementType: 'geometry',
              stylers: {
                color: '#fefefe'
              }
            },
            {
              featureType: 'arterial',
              elementType: 'geometry.fill',
              stylers: {
                color: '#fefefe'
              }
            },
            {
              featureType: 'poi',
              elementType: 'all',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'green',
              elementType: 'all',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'subway',
              elementType: 'all',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'manmade',
              elementType: 'all',
              stylers: {
                color: '#d1d1d1'
              }
            },
            {
              featureType: 'local',
              elementType: 'all',
              stylers: {
                color: '#d1d1d1'
              }
            },
            {
              featureType: 'arterial',
              elementType: 'labels',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'boundary',
              elementType: 'all',
              stylers: {
                color: '#fefefe'
              }
            },
            {
              featureType: 'building',
              elementType: 'all',
              stylers: {
                color: '#d1d1d1'
              }
            },
            {
              featureType: 'label',
              elementType: 'labels.text.fill',
              stylers: {
                color: '#999999'
              }
            }
          ]
        }
      },
      series: [
        {
          type: 'lines',
          coordinateSystem: 'bmap',
          polyline: true,
          data: busLines,
          silent: true,
          lineStyle: {
            color: 'rgb(200, 35, 45)',
            opacity: 0.2,
            width: 1
          },
          progressiveThreshold: 500,
          progressive: 200
        }
      ]
    })
  );
});
```
