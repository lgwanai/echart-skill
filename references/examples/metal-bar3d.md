# ä¸ç»´æ±ç¶å¾ - éå±è´¨æ

**Category:** `bar3D`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=metal-bar3d
**Template:** NONE — use knowledge base
**Data Format:** `N/A`
**Features:** per-item colors via itemStyle, emphasis/hover effects

## Official Option Code

```javascript
/*
title: Metal Bar3D
category: bar3D
titleCN: ä¸ç»´æ±ç¶å¾ - éå±è´¨æ
*/
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

## Placeholders

| Placeholder | Type | Description |
|-------------|------|-------------|
| `{{{TITLE}}}` | string | title |

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
