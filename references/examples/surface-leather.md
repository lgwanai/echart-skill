# surface-leather

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=surface-leather
**Chart Type:** `value`

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
title: Leather Material
category: surface
titleCN: ç®é©æè´¨
*/
var TILING = [4, 2];
var heightImg = new Image();
heightImg.onload = update;
heightImg.crossOrigin = 'anonymous';
heightImg.src = ROOT_PATH + '/data-gl/asset/leather/leather_height.jpg';
function update() {
  var canvas = document.createElement('canvas');
  var ctx = canvas.getContext('2d');
  var width = (canvas.width = heightImg.width);
  var height = (canvas.height = heightImg.height);
  ctx.drawImage(heightImg, 0, 0, width, height);
  var imgData = ctx.getImageData(0, 0, width, height).data;
  function getScale(u, v) {
    u = ((u / Math.PI) * 0.5 + 0.5) * TILING[0];
    v = (v / Math.PI) * TILING[1];
    u = Math.floor((u - Math.floor(u)) * (width - 1));
    v = Math.floor((1 - v + Math.floor(v)) * (height - 1));
    var idx = v * width + u;
    return 1 + imgData[idx * 4] / 255 / 20;
  }
  myChart.setOption({
    xAxis3D: {
      type: 'value',
      min: -1.5,
      max: 1.5
    },
    yAxis3D: {
      type: 'value',
      min: -1.5,
      max: 1.5
    },
    zAxis3D: {
      type: 'value',
      min: -1.5,
      max: 1.5
    },
    grid3D: {
      show: false,
      environment: 'none',
      axisPointer: {
        show: false
      },
      postEffect: {
        enable: true,
        screenSpaceAmbientOcclusion: {
          enable: true,
          radius: 10,
          intensity: 2,
          quality: 'high'
        },
        screenSpaceReflection: {
          enable: false
        },
        depthOfField: {
          enable: false,
          focalRange: 10,
          fstop: 4
        }
      },
      temporalSuperSampling: {
        enable: true
      },
      light: {
        main: {
          intensity: 2,
          shadow: true
        },
        ambient: {
          intensity: 0
        },
        ambientCubemap: {
          texture: ROOT_PATH + '/data-gl/asset/pisa.hdr',
          exposure: 1,
          diffuseIntensity: 1,
          specularIntensity: 2
        }
      },
      viewControl: {
        distance: 80
        // projection: 'orthographic'
      }
    },
    series: [
      {
        type: 'surface',
        parametric: true,
        shading: 'realistic',
        silent: true,
        wireframe: {
          show: false
        },
        realisticMaterial: {
          // detailTexture: 'asset/leather/leather_albedo.jpg',
          roughness: ROOT_PATH + '/data-gl/asset/leather/leather_roughness.jpg',
          normalTexture:
            ROOT_PATH + '/data-gl/asset/leather/leather_normal.jpg',
          textureTiling: TILING
        },
        itemStyle: {
          color: '#300'
        },
        parametricEquation: {
          u: {
            min: -Math.PI,
            max: Math.PI,
            step: Math.PI / 100
          },
          v: {
            min: 0.4,
            max: Math.PI - 0.4,
            step: Math.PI / 100
          },
          x: function (u, v) {
            return Math.sin(v) * Math.sin(u) * getScale(u, v);
          },
          y: function (u, v) {
            return Math.sin(v) * Math.cos(u) * getScale(u, v);
          },
          z: function (u, v) {
            return Math.cos(v) * getScale(u, v);
          }
        }
      }
    ]
  });
}
```
