# geo-svg-map

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=geo-svg-map
**Chart Type:** `scatter`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: need **x** + **y** columns (both numeric)
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

Data arrays to replace: **1**

## Reference Code

```javascript
/*
title: GEO SVG Map
category: map
titleCN: 地图（SVG）
*/
$.get(
  ROOT_PATH + '/data/asset/geo/Sicily_prehellenic_topographic_map.svg',
  function (svg) {
    echarts.registerMap('sicily', { svg: svg });
    option = {
      tooltip: {
        formatter: function (params) {
          console.log(params);
          return [
            params.name + ':',
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx'
          ].join('<br>');
        }
      },
      geo: [
        {
          map: 'sicily',
          roam: true,
          layoutCenter: ['50%', '50%'],
          layoutSize: '100%',
          selectedMode: 'single',
          tooltip: {
            show: true,
            confine: true,
            formatter: function (params) {
              return [
                'This is the introduction:',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx'
              ].join('<br>');
            }
          },
          itemStyle: {
            color: undefined
          },
          emphasis: {
            label: {
              show: false
            }
          },
          select: {
            itemStyle: {
              color: '#b50205'
            },
            label: {
              show: false
            }
          },
          regions: [
            {
              name: 'route1',
              itemStyle: {
                borderWidth: 0
              },
              select: {
                itemStyle: {
                  color: '#b5280d',
                  borderWidth: 0
                }
              },
              tooltip: {
                position: 'right',
                alwaysShowContent: true,
                enterable: true,
                extraCssText: 'user-select: text',
                formatter: [
                  'Route 1:',
                  'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxxxxxxxxxxxxxxx'
                ].join('<br>')
              }
            },
            {
              name: 'route2',
              itemStyle: {
                borderWidth: 0
              },
              select: {
                itemStyle: {
                  color: '#b5280d',
                  borderWidth: 0
                }
              },
              tooltip: {
                position: 'left',
                alwaysShowContent: true,
                enterable: true,
                extraCssText: 'user-select: text',
                formatter: [
                  'Route 2:',
                  'xxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxx'
                ].join('<br>')
              }
            }
          ]
        }
      ],
      // -------------
      // Make buttons
      grid: {
        top: 10,
        left: 'center',
        width: 80,
        height: 20
      },
      xAxis: {
        axisLine: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        axisTick: { show: false }
      },
      yAxis: {
        axisLine: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        axisTick: { show: false }
      },
      series: {
        type: 'scatter',
        itemStyle: {},
        label: {
          show: true,
          borderColor: '#999',
          borderWidth: 1,
          borderRadius: 2,
          backgroundColor: '#fff',
          padding: [3, 5],
          fontSize: 18,
          opacity: 1,
          color: '#333'
        },
        encode: {
          label: 2
        },
        symbolSize: 0,
        tooltip: { show: false },
        selectedMode: 'single',
        select: {
          label: {
            color: '#fff',
            borderColor: '#555',
            backgroundColor: '#555'
          }
        },
        data: [
          [0, 0, 'route1'],
          [1, 0, 'route2']
        ]
      }
      // Make buttons end
      // -----------------
    };
    myChart.setOption(option);
    myChart.on('selectchanged', function (params) {
      if (!params.selected.length) {
        myChart.dispatchAction({
          type: 'hideTip'
        });
        myChart.dispatchAction({
          type: 'geoSelect',
          geoIndex: 0
          // Use no name to unselect.
        });
      } else {
        var btnDataIdx = params.selected[0].dataIndex[0];
        var name = option.series.data[btnDataIdx][2];
        myChart.dispatchAction({
          type: 'geoSelect',
          geoIndex: 0,
          name: name
        });
        myChart.dispatchAction({
          type: 'showTip',
          geoIndex: 0,
          name: name
        });
      }
    });
  }
);
```
