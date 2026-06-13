# ç®é©æè´¨ / Leather Material

**Category:** `surface`
**Example dir:** `surface-leather`
**Difficulty:** 

## Template Match
- **3d/surface.html** — Surface

## Option Code
```javascript
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
            return Math.sin(v) * Math.cos(
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
- This is an official ECharts example from `surface-leather/main.js`
- Template data format: `equation.z as JS function`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
