# ç­å¼çº¿æ¸²æ / Contour Paint

**Category:** `globe`
**Example dir:** `globe-contour-paint`

## Template
- **3d/globe.html** — Globe
Data format: `[[lat, lng, value], ...]`

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
  
```

## Key Points
- Generate via: `scripts/build_template.py 3d/globe.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
