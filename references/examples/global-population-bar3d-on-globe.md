# å¨çäººå£åå¸ - å°çä¸ç Bar3D / Global Population - Bar3D on Globe

**Category:** `bar3D`
**Example dir:** `global-population-bar3d-on-globe`
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
  option = {
    backgroundColor: '#000',
    globe: {
      baseTexture: ROOT_PATH + '/data-gl/asset/world.topo.bathy.200401.jpg',
      heightTexture: ROOT_PATH + '/data-gl/asset/world.topo.bathy.200401.jpg',
      shading: 'lambert',
      environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
      light: {
        main: {
          intensity: 2
        }
      },
      viewControl: {
        autoRotate: false
      }
    },
    visualMap: {
      max: 40,
      calculable: true,
      realtime: false,
      inRange: {
        colorLightness: [0.2, 0.9]
      },
      textStyle: {
        color: '#fff'
      },
      controller: {
        inRange: {
          color: 'orange'
        }
      },
      outOfRange: {
        colorAlpha: 0
      }
    },
    series: [
      {
        type: 'bar3D',
        coordinateSystem: 'globe',
        data: data,
        barSize: 0.6,
        minHeight: 0.2,
        silent: true,
        itemStyle: {
          color: 'orange'
        }
      }
    ]
  };
  myChart.setOption(option);
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
- This is an official ECharts example from `global-population-bar3d-on-globe/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
