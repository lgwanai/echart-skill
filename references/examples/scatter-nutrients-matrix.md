# 营养分布散点矩阵 / Scatter Nutrients Matrix

**Category:** `scatter`
**Example dir:** `scatter-nutrients-matrix`
**Difficulty:** 7

## Template Match
- **3d/scatter3d.html** — Scatter3D

## Option Code
```javascript
const indices = {
  name: 0,
  group: 1,
  id: 16
};
const schema = [
  { name: 'name', index: 0 },
  { name: 'group', index: 1 },
  { name: 'protein', index: 2 },
  { name: 'calcium', index: 3 },
  { name: 'sodium', index: 4 },
  { name: 'fiber', index: 5 },
  { name: 'vitaminc', index: 6 },
  { name: 'potassium', index: 7 },
  { name: 'carbohydrate', index: 8 },
  { name: 'sugars', index: 9 },
  { name: 'fat', index: 10 },
  { name: 'water', index: 11 },
  { name: 'calories', index: 12 },
  { name: 'saturated', index: 13 },
  { name: 'monounsat', index: 14 },
  { name: 'polyunsat', index: 15 },
  { name: 'id', index: 16 }
];
const axisColors = {
  xAxisLeft: '#2A8339',
  xAxisRight: '#367DA6',
  yAxisTop: '#A68B36',
  yAxisBottom: '#BD5692'
};
const colorBySchema = {};
const fieldIndices = schema.reduce(function (obj, item) {
  obj[item.name] = item.index;
  return obj;
}, {});
const groupCategories = [];
const groupColors = [];
let data;
// zlevel 为 1 的层开启尾迹特效
myChart.getZr().configLayer(1, {
  motionBlur: true
});
function normalizeData(originData) {
  let groupMap = {};
  originData.forEach(function (row) {
    let groupName = row[indices.group];
    if (!groupMap.hasOwnProperty(groupName)) {
      groupMap[groupName] = 1;
    }
  });
  originData.forEach(function (row) {
    row.forEach(function (item, index) {
      if (
        index !== indices.name &&
        index !== indices.group &&
        index !== indices.id
      ) {
        // Convert null to zero, as all of them under unit "g".
        row[index] = parseFloat(item) || 0;
      }
    });
  });
  for (let groupName in groupMap) {
    if (groupMap.hasOwnProperty(groupName)) {
      groupCategories.push(groupName);
    }
  }
  let hStep = Math.round(300 / (groupCategories.length - 1));
  for (let i = 0; i < groupCategories.length; i++) {
    groupColors.push(echarts.color.modifyHSL('#5A94DF', hStep * i));
  }
  return originData;
}
function makeAxis(dimIndex, id, name, nameLocation) {
  const axisColor = axisColors[id.split('-')[dimIndex]];
  colorBySchema[name] = axisColor;
  return {
    id: id,
    name: name,
    nameLocation: nameLocation,
    nameGap: nameLocation === 'middle' ? 30 : 10,
    gridId: id,
    splitLine: { show: false },
    axisLine: {
      lineStyle: {
        color: axisColor
      }
    },
    axisLabel: {
      color: axisColor
    },
    axisTick: {
      lineStyle: {
        color: axisColor
      }
    }
  };
}
function makeSeriesData(xLeftOrRight, yTopOrBottom) {
  return data.map(function (item, idx) {
    const schemaX = app.config[xLeftOrRight];
    const schemaY = app.config[yTopOrBottom];
    return [
      item[fieldIndices[schemaX]],
      item[fieldIndices[schemaY]],
      item[1],
      item[0],
      schemaX,
      schemaY,
      idx // 6
    ];
  });
}
function makeSeries(xLeftOrRight, yTopOrBottom) {
  let id = xLeftOrRight + '-' + yTopOrBottom;
  return {
    zlevel: 1,
    type: 'scatter',
    name: 'nutrients',
    xAxisId: id,
    yAxis
```

## Relevant Debug Patterns
## #18
 — Scatter Geo/Map 空白：MAP_INLINE 被替换导致地图未加载
- **日期**：2026-06-13
- **现象**：12_Scatter_Geo、13_Map_China 等地图类图表空白
- **根因**：数据 dict 中 `"MAP_INLINE": ""` → `_json_safe` 替换 `{{MAP_INLINE}}` 为 `''` → `<!-- {{MAP_INLINE}} -->` 变成 `<!-- '' -->` → `build_template.py` 的地图注入检测 `if "<!-- {{MAP_INLINE}} -->" in html` 失败 → China GeoJSON 未嵌入 → 地图空白
- **修复**：**不要在数据 dict 中提供 `MAP_INLINE`/`GL_INLINE`/`ECHARTS_INLINE` 这三个特殊占位符**。它们由 `build_template.py` 自动处理（代码中已排除此三类占位符的校验）。**模板不需要修改**——模板中的 `<!-- {{MAP_INLINE}} --...

## #19
 — Scatter Geo 气泡大小无差异
- **日期**：2026-06-13
- **现象**：12_Scatter_Geo 所有气泡一样大
- **根因**：模板 `symbolSize: function(val) { return Math.sqrt(val[2]) / SIZE_SCALE || 8; }` 中 `Math.sqrt` 压缩了数值差异。值 70-100 经 sqrt 后为 8.4-10，差值仅 1.6px，肉眼不可分辨
- **修复**：模板改为 `val[2] / {{SIZE_SCALE}}`（线性），SIZE_SCALE=5 → 14-20px 可分辨范围

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
- This is an official ECharts example from `scatter-nutrients-matrix/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
