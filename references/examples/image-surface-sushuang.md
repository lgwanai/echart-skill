# Image Surface Sushuang / Image Surface Sushuang

**Category:** `surface`
**Example dir:** `image-surface-sushuang`
**Difficulty:** 

## Template Match
- **3d/surface.html** — Surface

## Option Code
```javascript
var img = new Image();
var canvas = document.createElement('canvas');
var ctx = canvas.getContext('2d');
img.onload = function () {
  var width = (canvas.width = img.width);
  var height = (canvas.height = img.height);
  ctx.drawImage(img, 0, 0, width, height);
  var imgData = ctx.getImageData(0, 0, width, height);
  var data = [];
  for (var i = 0; i < imgData.data.length / 4; i++) {
    var r = imgData.data[i * 4];
    var g = imgData.data[i * 4 + 1];
    var b = imgData.data[i * 4 + 2];
    var lum = 255 - (0.2125 * r + 0.7154 * g + 0.0721 * b);
    lum = (lum - 125) / 10 + 50;
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
        axisPointer: {
          show: false
        },
        viewControl: {
          distance: 100
        },
        postEffect: {
          enable: true
        },
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
          type: 'surface',
          silent: true,
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
  'data:image/jpeg;charset=utf-8;base64,/9j/4AAQSkZJRgABAQABXgFeAAD/4QFURXhpZgAATU0AKgAAAAgACAEGAAMAAAABAAIAAAESAAMAAAABAAEAAAEaAAUAAAABAAAAbgEbAAUAAAABAAAAdgEoAAMAAAABAAIAAAExAAIAAAAgAAAAfgEyAAIAAAAUAAAAnodpAAQAAAABAAAAsgAAAAAAAAFeAAAAAQAAAV4AAAABQWRvYmUgUGhvdG9zaG9wIENTNiAoTWFjaW50b3NoKQAyMDE3OjA0OjExIDIyOjAxOjUwAAAJkAAABwAAAAQwMjIxkAMAAgAAABQAAAEkkAQAAgAAABQAAAE4kQEABwAAAAQBAgMAoAAABwAAAAQwMTAwoAEAAwAAAAEAAQAAoAIABAAAAAEAAAEAoAMABAAAAAEAAAFJpAYAAwAAAAEAAAAAAAAAADIwMTc6MDM6MTUgMTE6MTE6MDEAMjAxNzowMzoxNSAxMToxMTowMQD/4Q4RaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLwA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/PiA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA1LjQuMCI+IDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+IDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIiB4bWxuczpzdEV2dD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlRXZlbnQjIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHh
```

## Relevant Debug Patterns
## #28
 — 3D Scatter/Surface/Globe/Lines3D 同样空白
- **日期**：2026-06-13
- **现象**：34/35/36/37 全部空白
- **根因**：与 #27 相同——GL_INLINE 破坏注入 + 模板配置偏离官方示例。所有 3D 模板统一修复
- **修复**：3d/scatter3d.html、3d/surface.html、3d/globe.html、3d/lines3d.html 全部改为与官方示例一致的配置。关键：`zAxis3D: {}`（非 `{type:'value'}`）、`grid3D: {}`、无 `coordinateSystem`

---
...

## #29
 — Surface 空白：JS 函数被 `_json_safe` 加引号变成字符串
- **日期**：2026-06-13
- **现象**：35_3D_Surface 空白，JS 函数 `function(x,y){...}` 被当成字符串输出 `'function(x,y){...}'`
- **根因**：`build_template.py` 的 `_json_safe` 不支持函数字符串，所有字符串值都被包在引号中
- **修复**：(1) `_json_safe` 新增检测：以 `function` 或 `(` 开头的字符串直接原样返回；(2) surface 模板改为与官方示例一致的 `equation: {x,y,z}` 结构

---
...

## Key Points
- This is an official ECharts example from `image-surface-sushuang/main.js`
- Template data format: `equation.z as JS function`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
