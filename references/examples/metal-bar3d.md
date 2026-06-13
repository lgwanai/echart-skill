# ä¸ç»´æ±ç¶å¾ - éå±è´¨æ / Metal Bar3D

**Category:** `bar3D`
**Example dir:** `metal-bar3d`
**Difficulty:** 

## Template Match
- **3d/bar3d.html** — Bar3D

## Option Code
```javascript
$.getScript(CDN_PATH + 'simplex-noise@2.4.0/simplex-noise.js').done(
  function () {
    var noise = new SimplexNoise(Math.random);
    function generateData(theta, min, max) {
      var data = [];
      for (var i = 0; i <= 20; i++) {
        for (var j = 0; j <= 20; j++) {
          var value = noise.noise2D(i / 20, j / 20);
          valMax = Math.max(valMax, value);
          valMin = Math.min(valMin, value);
          data.push([i, j, value * 2 + 4]);
        }
      }
      return data;
    }
    var valMin = Infinity;
    var valMax = -Infinity;
    var data = generateData(2, -5, 5);
    myChart.setOption(
      (option = {
        tooltip: {},
        xAxis3D: {
          type: 'value'
        },
        yAxis3D: {
          type: 'value'
        },
        zAxis3D: {
          type: 'value',
          max: 10,
          min: 0
        },
        grid3D: {
          environment: '#000',
          axisPointer: {
            show: false
          },
          postEffect: {
            enable: true,
            SSAO: {
              enable: true,
              radius: 5
            }
          },
          light: {
            main: {
              intensity: 3
            },
            ambientCubemap: {
              texture: ROOT_PATH + '/data-gl/asset/pisa.hdr',
              exposure: 1,
              diffuseIntensity: 0.5,
              specularIntensity: 2
            }
          }
        },
        series: [
          {
            type: 'bar3D',
            data: data,
            barSize: 4,
            bevelSize: 0.4,
            bevelSmoothness: 4,
            shading: 'realistic',
            realisticMaterial: {
              roughness: 0.3,
              metalness: 1
            },
            label: {
              textStyle: {
                fontSize: 16,
                borderWidth: 1
              }
            },
            itemStyle: {
              color: '#ccc'
            },
            emphasis: {
              label: {
                show: false
              }
            }
          }
        ]
      })
    );
  }
);
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
- This is an official ECharts example from `metal-bar3d/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
