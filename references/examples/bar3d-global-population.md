# bar3d-global-population

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar3d-global-population

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Bar3D - Global Population
category: bar3D
titleCN: Bar3D - å¨çäººå£åå¸
*/
$.getJSON(ROOT_PATH + '/data-gl/asset/data/population.json', function (data) {
  data = data
    .filter(function (dataItem) {
      return dataItem[2] > 0;
    })
    .map(function (dataItem) {
      return [dataItem[0], dataItem[1], Math.sqrt(dataItem[2])];
    });
  myChart.setOption({
    backgroundColor: '#cdcfd5',
    geo3D: {
      map: 'world',
      shading: 'lambert',
      light: {
        main: {
          intensity: 5,
          shadow: true,
          shadowQuality: 'high',
          alpha: 30
        },
        ambient: {
          intensity: 0
        },
        ambientCubemap: {
          texture: ROOT_PATH + '/data-gl/asset/canyon.hdr',
          exposure: 1,
          diffuseIntensity: 0.5
        }
      },
      viewControl: {
        distance: 50,
        panMouseButton: 'left',
        rotateMouseButton: 'right'
      },
      groundPlane: {
        show: true,
        color: '#999'
      },
      postEffect: {
        enable: true,
        bloom: {
          enable: false
        },
        SSAO: {
          radius: 1,
          intensity: 1,
          enable: true
        },
        depthOfField: {
          enable: false,
          focalRange: 10,
          blurRadius: 10,
          fstop: 1
        }
      },
      temporalSuperSampling: {
        enable: true
      },
      itemStyle: {},
      regionHeight: 2
    },
    visualMap: {
      max: 40,
      calculable: true,
      realtime: false,
      inRange: {
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
      outOfRange: {
        colorAlpha: 0
      }
    },
    series: [
      {
        type: 'bar3D',
        coordinateSystem: 'geo3D',
        shading: 'lambert',
        data: data,
        barSize: 0.1,
        minHeight: 0.2,
        silent: true,
        itemStyle: {
          color: 'orange'
          // opacity: 0.8
        }
      }
    ]
  });
});
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
