# 六边形分箱图（自定义系列） / Hexagonal Binning

**Category:** `custom, map`
**Example dir:** `custom-hexbin`
**Difficulty:** 6

## Template Match
- **geo/lines.html** — 

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
    hexagonRadiusInGeo
  );
  var data = hexBinResult.bins.map(function (bin) {
    var made = 0;
    bin.points.forEach(function (point) {
      made += point[2];
    });
    return [
      bin.x,
      bin.y,
      bin.points.length,
      ((made / bin.points.length) * 100).toFixed(2)
    ];
  });
  function renderItemHexBin(params, api) {
    var center = api.coord([api.value(0), api.value(1)]);
    var points = [];
    var pointsBG = [];
    var maxViewRadius = api.size([hexagonRadiusInGeo, 0])[0];
    var minViewRadius = Math.min(maxViewRadius, 4);
    var extentMax = Math.log(Math.sqrt(hexBinResult.maxBinLen));
    var viewRadius = echarts.number.linearMap(
      Math.log(Math.sqrt(api.value(2))),
      [0, extentMax],
      [minViewRadius, maxViewRadius]
    );
    var angle = Math.PI / 6;
    for (var i = 0; i < 6; i++, angle += Math.PI / 3) {
      points.push([
        center[0] + viewRadius * Math.cos(angle),
        center[1] + viewRadius * Math.sin(angle)
      ]);
      pointsBG.push([
     
```

## Relevant Debug Patterns
## #18
 — Scatter Geo/Map 空白：MAP_INLINE 被替换导致地图未加载
- **日期**：2026-06-13
- **现象**：12_Scatter_Geo、13_Map_China 等地图类图表空白
- **根因**：数据 dict 中 `"MAP_INLINE": ""` → `_json_safe` 替换 `{{MAP_INLINE}}` 为 `''` → `<!-- {{MAP_INLINE}} -->` 变成 `<!-- '' -->` → `build_template.py` 的地图注入检测 `if "<!-- {{MAP_INLINE}} -->" in html` 失败 → China GeoJSON 未嵌入 → 地图空白
- **修复**：**不要在数据 dict 中提供 `MAP_INLINE`/`GL_INLINE`/`ECHARTS_INLINE` 这三个特殊占位符**。它们由 `build_template.py` 自动处理（代码中已排除此三类占位符的校验）。**模板不需要修改**——模板中的 `<!-- {{MAP_INLINE}} --...

## #20
 — Treemap 父节点缺少 value 导致布局错误
- **日期**：2026-06-13
- **现象**：19_Treemap 布局比例失调，标签只显示根节点名称
- **根因**：(1) 父节点没有 `value` 属性，ECharts treemap 无法按比例分配面积；(2) 数据只有 2 大类 4 项，过于稀疏；(3) `UPPER_LABEL_SHOW: false` 导致上层标签不显示
- **修复**：(1) 父节点添加 `value`（子节点之和）；(2) 扩充为 3 大类 11 项；(3) `UPPER_LABEL_SHOW: true`；(4) **模板增加防御**：`upperLabel.show` 和 `breadcrumb.show` 在值为空时默认为 `true`

---
...

## #25
 — EffectScatter 空白 + 颜色不生效
- **日期**：2026-06-13
- **现象**：30_EffectScatter 一片空白，修复后各城市同色
- **根因**：(1) `GEO_COORD_MAP: "{}"` 空对象，`MAP_NAME: ""` 空地图名 → 无地图；(2) `convertData()` 只复制 `name`/`value`，丢弃 `itemStyle`
- **修复**：(1) 提供真实 GEO_COORD_MAP + MAP_NAME="china"；(2) `convertData` 保留 `itemStyle`；(3) 每城市设不同颜色 `itemStyle.color`；(4) **模板守卫**：`geoCoordMap || {}`，`map || "china"`

---
...

## Key Points
- This is an official ECharts example from `custom-hexbin/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
