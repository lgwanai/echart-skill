# å¾åè½¬ä¸ç»´æ±ç¶å¾ / Image to Bar3D

**Category:** `bar3D`
**Example dir:** `image-to-bar3d`
**Difficulty:** 

## Template Match
- **3d/bar3d.html** — Bar3D

## Option Code
```javascript
var img = new Image();
var canvas = document.createElement('canvas');
var ctx = canvas.getContext('2d');
img.onload = function () {
  var width = (canvas.width = img.width / 2);
  var height = (canvas.height = img.height / 2);
  ctx.drawImage(img, 0, 0, width, height);
  var imgData = ctx.getImageData(0, 0, width, height);
  var data = [];
  for (var i = 0; i < imgData.data.length / 4; i++) {
    var r = imgData.data[i * 4];
    var g = imgData.data[i * 4 + 1];
    var b = imgData.data[i * 4 + 2];
    var lum = 255 - (0.2125 * r + 0.7154 * g + 0.0721 * b);
    lum = (lum - 125) / 20 + 50;
    data.push([i % width, height - Math.floor(i / width), lum]);
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
        viewControl: {
          alpha: 20,
          beta: -30
        },
        postEffect: {
          enable: true,
          SSAO: {
            enable: true
          }
        },
        boxDepth: 120,
        light: {
          main: {
            shadow: true,
            intensity: 2
          },
          ambientCubemap: {
            texture: ROOT_PATH + '/data-gl/asset/canyon.hdr',
            exposure: 2,
            diffuseIntensity: 0.2,
            specularIntensity: 1
          }
        }
      },
      series: [
        {
          type: 'bar3D',
          shading: 'realistic',
          barSize: 1,
          wireframe: {
            show: false
          },
          itemStyle: {
            color: function (params) {
              var i = params.dataIndex;
              var r = imgData.data[i * 4];
              var g = imgData.data[i * 4 + 1];
              var b = imgData.data[i * 4 + 2];
              return 'rgb(' + [r, g, b].join(',') + ')';
            }
          },
          data: data
        }
      ]
    })
  );
};
img.src =
  'data:image/jpeg;charset=utf-8;base64,/9j/4RtXRXhpZgAATU0AKgAAAAgADQEAAAMAAAABBmAAAAEBAAMAAAABCZAAAAECAAMAAAADAAAAqgEGAAMAAAABAAIAAAESAAMAAAABAAEAAAEVAAMAAAABAAMAAAEaAAUAAAABAAAAsAEbAAUAAAABAAAAuAEoAAMAAAABAAIAAAExAAIAAAAgAAAAwAEyAAIAAAAUAAAA4AITAAMAAAABAAEAAIdpAAQAAAABAAAA9AAAAZwACAAIAAgANWfgAAAnEAA1Z+AAACcQQWRvYmUgUGhvdG9zaG9wIENTNiAoTWFjaW50b3NoKQAyMDE3OjA0OjExIDIyOjI4OjQxAAAJkAAABwAAAAQwMjIxkAMAAgAAABoAAAFmkAQAAgAAABoAAAGAkQEABwAAAAQBAgMAoAAABwAAAAQwMTAwoAEAAwAAAAEAAQAAoAIABAAAAAEAAADIoAMABAAAAAEAAADqpAYAAwAAAAEAAAAAAAAAADIwMTc6MDM6MTUgMTI6MDU6NDDkuIvljYgAMjAxNzowMzoxNSAxMjowNTo0MOS4i+WNiAAAAAAGAQMAAwAAAAEABgAAARoABQAAAAEAAAHqARsABQAAAAEAAAHyASgAAwAAAAEAAgAAAgEABAAAAAEAAAH6AgIABAAAAAEAABlVAAAAAAAAAEgAAAABAAAASAAAAAH/2P/tAAxBZG9iZV9DTQAB/+4ADkFkb2JlAGSAAAAAAf/bAIQADAgICAkIDAkJDBELCgsRFQ8MDA8VGBMTFRMTGBEMDAwMDAwRDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAENCwsNDg0QDg4QFA4ODhQUDg4ODhQRDAwMDAwREQwMDAwMDBEMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwM/8AAEQgAoACJAwEiAAIRAQMRAf/
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
- This is an official ECharts example from `image-to-bar3d/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
