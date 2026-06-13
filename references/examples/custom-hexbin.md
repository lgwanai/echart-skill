# 六边形分箱图（自定义系列） / Hexagonal Binning

**Category:** `custom, map`
**Example dir:** `custom-hexbin`

## Template
- **custom/error-bar.html** — Error Bar
Data format: `[[xIdx, val, lowVal, highVal], ...]`

## Option Code
```javascript
// Hexbin statistics code based on [d3-hexbin](https://github.com/d3/d3-hexbin)
function hexBinStatistics(points, r) {
  var dx = r * 2 * Math.sin(Math.PI / 3);
  var dy = r * 1.5;
  var binsById = {};
  var bins = [];
  for (var i = 0, n = points.length; i < n; ++i) {
    var point = points[i];
    var px = point[0];
    var py = point[1];
    if (isNaN(px) || isNaN(py)) {
      continue;
    }
    var pj = Math.round((py = py / dy));
    var pi = Math.round((px = px / dx - (pj & 1) / 2));
    var py1 = py - pj;
    if (Math.abs(py1) * 3 > 1) {
      var px1 = px - pi;
      var pi2 = pi + (px < pi ? -1 : 1) / 2;
      var pj2 = pj + (py < pj ? -1 : 1);
      var px2 = px - pi2;
      var py2 = py - pj2;
      if (px1 * px1 + py1 * py1 > px2 * px2 + py2 * py2) {
        pi = pi2 + (pj & 1 ? 1 : -1) / 2;
        pj = pj2;
      }
    }
    var id = pi + '-' + pj;
    var bin = binsById[id];
    if (bin) {
      bin.points.push(point);
    } else {
      bins.push((bin = binsById[id] = { points: [point] }));
      bin.x = (pi + (pj & 1) / 2) * dx;
      bin.y = pj * dy;
    }
  }
  var maxBinLen = -Infinity;
  for (var i = 0; i < bins.length; i++) {
    maxBinLen = Math.max(maxBinLen, bins.length);
  }
  return {
    maxBinLen: maxBinLen,
    bins: bins
  };
}
$.when(
  $.getJSON(ROOT_PATH + '/data/asset/data/kawhi-leonard-16-17-regular.json'),
  $.getJSON(ROOT_PATH + '/data/asset/data/nba-court.json')
).done(function (shotData, nbaCourt) {
  shotData = shotData[0];
  nbaCourt = nbaCourt[0];
  echarts.registerMap('nbaCourt', nbaCourt.borderGeoJSON);
  var backgroundColor = '#333';
  var hexagonRadiusInGeo = 1;
  var hexBinResult = hexBinStatistics(
    shotData.data.map(function (item) {
      // "shot_made_flag" made missed
      var made = item[shotData.schema.indexOf('shot_made_flag')];
      return [
        item[shotData.schema.indexOf('loc_x')],
        item[shotData.schema.indexOf('loc_y')],
        made === 'made' ? 1 : 0
      ];
    }),
    hexagonRadiusInG
```

## Key Points
- Generate via: `scripts/build_template.py custom/error-bar.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
