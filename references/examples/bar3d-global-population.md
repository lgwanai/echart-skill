# Bar3D - å¨çäººå£åå¸ / Bar3D - Global Population

**Category:** `bar3D`
**Example dir:** `bar3d-global-population`
**Difficulty:** 

## Template Match
- **3d/bar3d.html** — Bar3D

## Option Code
```javascript
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

## Relevant Debug Patterns
## #27
 — 3D Bar 空白：GL_INLINE + coordinateSystem + zAxis3D 配置错误
- **日期**：2026-06-13
- **现象**：33_3D_Bar 一片空白
- **根因**：(1) `GL_INLINE: ""` 破坏 echarts-gl 注入（同 #18）；(2) `coordinateSystem: 'cartesian3D'` + `zAxis3D: {type:'value'}` + `shading:'realistic'` 不是官方推荐的配置组合；(3) 官方示例用 `zAxis3D: {}`（空对象）、无 `coordinateSystem`、`shading: 'lambert'`
- **修复**：模板改为与 ECharts 官方 bar3D 示例完全一致的配置：`grid3D: {}`、`zAxis3D: {}`、`shading: 'lambert'`、无 `coordinateSystem`、无 `barSize`

---
...

## Key Points
- This is an official ECharts example from `bar3d-global-population/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
