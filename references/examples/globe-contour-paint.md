# ç­å¼çº¿æ¸²æ / Contour Paint

**Category:** `globe`
**Example dir:** `globe-contour-paint`
**Difficulty:** 

## Template Match
- **3d/globe.html** — Globe

## Option Code
```javascript
var config = {
  color: '#c0101a',
  levels: 50,
  intensity: 100,
  threshold: 0.01
};
var canvas = document.createElement('canvas');
canvas.width = 4096;
canvas.height = 2048;
context = canvas.getContext('2d');
context.lineWidth = 0.4;
context.strokeStyle = config.color;
context.fillStyle = config.color;
context.shadowColor = config.color;
$.when(
  $.getScript(CDN_PATH + 'd3-array@2.8.0/dist/d3-array.js'),
  $.getScript(CDN_PATH + 'd3-contour@2.0.0/dist/d3-contour.js'),
  $.getScript(CDN_PATH + 'd3-geo@2.0.1/dist/d3-geo.js'),
  $.getScript(CDN_PATH + 'd3-timer@2.0.0/dist/d3-timer.js')
).done(function () {
  image(ROOT_PATH + '/data-gl/asset/bathymetry_bw_composite_4k.jpg').then(
    function (image) {
      var m = image.height,
        n = image.width,
        values = new Array(n * m),
        contours = d3.contours().size([n, m]).smooth(true),
        projection = d3.geoIdentity().scale(canvas.width / n),
        path = d3.geoPath(projection, context);
      //   StackBlur.R(image, 5);
      for (var j = 0, k = 0; j < m; ++j) {
        for (var i = 0; i < n; ++i, ++k) {
          values[k] = image.data[k << 2] / 255;
        }
      }
      var opt = {
        image: canvas
      };
      var results = [];
      function update(threshold, levels) {
        context.clearRect(0, 0, canvas.width, canvas.height);
        var thresholds = [];
        for (var i = 0; i < levels; i++) {
          thresholds.push((threshold + (1 / levels) * i) % 1);
        }
        results = contours.thresholds(thresholds)(values);
        redraw();
      }
      function redraw() {
        results.forEach(function (d, idx) {
          context.beginPath();
          path(d);
          context.globalAlpha = 1;
          context.stroke();
          if (idx > (config.levels / 5) * 3) {
            context.globalAlpha = 0.01;
            context.fill();
          }
        });
        onupdate();
      }
      update(config.threshold, config.levels);
      initCharts(opt);
    }
  );
  function image(url) {
    return new Promise(function (resolve) {
      var image = new Image();
      image.src = url;
      image.crossOrigin = 'Anonymous';
      image.onload = function () {
        var canvas = document.createElement('canvas');
        canvas.width = image.width / 4;
        canvas.height = image.height / 4;
        var context = canvas.getContext('2d');
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
        resolve(context.getImageData(0, 0, canvas.width, canvas.height));
      };
    });
  }
  var contourChart = echarts.init(document.createElement('canvas'), null, {
    width: 4096,
    height: 2048
  });
  var img = new echarts.graphic.Image({
    style: {
      x: -1,
      y: -1
    }
  });
  onupdate = function () {
    img.dirty();
  };
  function initCharts(opt) {
    img.style.width = opt.image.width + 2;
    img.style.height = opt.image.height + 2;
    img.style.image = opt.image;
    contourChart.getZr().add(img);
    myChart.setOpt
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

## #30
 — Globe 无纹理显示为纯色/空白球
- **日期**：2026-06-13
- **现象**：36_3D_Globe 显示为纯蓝/黄色球，无地球纹理
- **根因**：未提供 `baseTexture`，ECharts globe 渲染为无纹理球体
- **修复**：下载 ECharts 官方示例的 1.3MB JPG 地球纹理（`echarts.apache.org/examples/data-gl/asset/world.topo.bathy.200401.jpg`），base64 嵌入为 `baseTexture`

---
...

## Key Points
- This is an official ECharts example from `globe-contour-paint/main.js`
- Template data format: `[[lat, lng, value], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
