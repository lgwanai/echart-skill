# bar3d-myth

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar3d-myth
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
title: Bar3D - Myth
category: bar3D
titleCN: Bar3D - æäº
*/
var img = new Image();
var canvas = document.createElement('canvas');
var ctx = canvas.getContext('2d');
img.onload = function () {
  var width = (canvas.width = img.width);
  var height = (canvas.height = img.height);
  ctx.drawImage(img, 0, 0, width, height);
  var imgData = ctx.getImageData(0, 0, width, height);
  var data = new Float32Array((imgData.data.length / 4) * 3);
  var off = 0;
  for (var i = 0; i < imgData.data.length / 4; i++) {
    var r = imgData.data[i * 4];
    var g = imgData.data[i * 4 + 1];
    var b = imgData.data[i * 4 + 2];
    var lum = 0.2125 * r + 0.7154 * g + 0.0721 * b;
    lum = (lum - 125) / 4 + 50;
    data[off++] = i % width;
    data[off++] = height - Math.floor(i / width);
    data[off++] = lum;
  }
  myChart.setOption(
    (option = {
      tooltip: {},
      backgroundColor: '#fff',
      xAxis3D: {
        type: 'value'
      },
      yAxis3D: {
        type: 'value'
      },
      zAxis3D: {
        type: 'value',
        min: 0,
        max: 100
      },
      grid3D: {
        show: false,
        viewControl: {
          alpha: 70,
          beta: 0
        },
        postEffect: {
          enable: true,
          depthOfField: {
            enable: true,
            blurRadius: 4,
            fstop: 10
          }
          // SSAO: {
          //     enable: true
          // }
        },
        boxDepth: 100,
        boxHeight: 20,
        environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
        light: {
          main: {
            shadow: true,
            intensity: 2
          },
          ambientCubemap: {
            texture: ROOT_PATH + '/data-gl/asset/canyon.hdr',
            exposure: 2,
            diffuseIntensity: 0.2
          }
        }
      },
      series: [
        {
          type: 'bar3D',
          shading: 'lambert',
          barSize: 0.8,
          silent: true,
          dimensions: ['x', 'y', 'z'],
          itemStyle: {
            color: function (params) {
              var i = params.dataIndex;
              var r = imgData.data[i * 4] / 255;
              var g = imgData.data[i * 4 + 1] / 255;
              var b = imgData.data[i * 4 + 2] / 255;
              var lum = 0.2125 * r + 0.7154 * g + 0.0721 * b;
              r *= lum * 2;
              g *= lum * 2;
              b *= lum * 2;
              return [r, g, b, 1];
            }
          },
          data: data
        }
      ]
    })
  );
};
img.src = ROOT_PATH + '/data-gl/asset/sample.jpg';
img.crossOrigin = 'Anonymous';
```
