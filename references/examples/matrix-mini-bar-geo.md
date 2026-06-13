# 矩阵坐标系下的微型条形图和地图 / Mini Bars and Geo in Matrix

**Category:** `matrix, bar, geo`
**Example dir:** `matrix-mini-bar-geo`
**Difficulty:** 6

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
var _colHeaders = ['Region and Time', 'Data A', 'Data B', 'Location'];
var _regionColIdx = 0;
var _geoColIdx = 3;
var _dataSourceList = [
  {
    name: '2021',
    data: [
      // 'Region', 'Data A', 'Data B'
      ['Valais', 1212, 2321],
      ['Ticino', 7181, 2114],
      ['Graubünden', 2763, 4212],
      ['Uri', 6122, 2942],
      ['Lucerne', 4221, 3411],
      ['Neuchâtel', 7221, 5121],
      ['Jura', 5121, 4121],
      ['Vaud', 6121, 3121],
      ['Thurgau', 7121, 2121],
      ['Schwyz', 8121, 1121]
    ]
  },
  {
    name: '2020',
    data: [
      // 'Region', 'Data A', 'Data B'
      ['Valais', 1010, 2221],
      ['Ticino', 7040, 1810],
      ['Graubünden', 2313, 4011],
      ['Uri', 6011, 2749],
      ['Lucerne', 3329, 3015],
      ['Neuchâtel', 7116, 4822],
      ['Jura', 4968, 3820],
      ['Vaud', 6027, 2928],
      ['Thurgau', 7011, 1725],
      ['Schwyz', 7311, 825]
    ]
  }
];
var _colorList = [
  '#ffd10a',
  '#0ca8df',
  '#b6d634',
  '#3fbe95',
  '#5070dd',
  '#ff994d',
  '#505372',
  '#fb628b',
  '#785db0'
];
function createChart() {
  option = {
    matrix: {
      x: {
        levelSize: 40,
        data: _colHeaders.map(function (item, colIdx) {
          return {
            value: item,
            size:
              colIdx === _geoColIdx
                ? '15%'
                : colIdx === _regionColIdx
                ? 120
                : undefined
          };
        }),
        itemStyle: { color: '#f0f8ff' },
        label: { fontWeight: 'bold' }
      },
      y: {
        data: _dataSourceList[0].data.map(function () {
          return '_'; // Any value is fine here, as we will not use it.
        }),
        show: false
      },
      body: {
        data: []
      },
      top: 25
    },
    legend: {},
    tooltip: {},
    grid: [],
    xAxis: [],
    yAxis: [],
    geo: [],
    series: []
  };
  // Assume every dataSourceList[i] has the same length; just for simplicity in this demo.
  var rowCount = _dataSourceList[0].data.length;
  for (var dataColIdx = 0; dataColIdx < _colHeaders.length; ++dataColIdx) {
    var dataExtentOnCol =
      dataColIdx === _regionColIdx || dataColIdx === _geoColIdx
        ? null
        : calculateDataExtentOnCol(_dataSourceList, dataColIdx);
    for (var dataRowIdx = 0; dataRowIdx < rowCount; ++dataRowIdx) {
      if (dataColIdx === _regionColIdx) {
        addCellPlainText(option, _dataSourceList, dataColIdx, dataRowIdx);
      } else if (dataColIdx === _geoColIdx) {
        addCellMiniGeo(option, _dataSourceList, dataColIdx, dataRowIdx);
      } else {
        addCellMiniBar(
          option,
          _dataSourceList,
          dataColIdx,
          dataRowIdx,
          dataExtentOnCol
        );
      }
    }
  }
  myChart.setOption(option);
}
function calculateDataExtentOnCol(dataSourceList, colIdx) {
  var min = Infinity;
  var max = -Infinity;
  dataSourceList.forEach((dataSource) => {
    dataSource.data.forEach((dataRow) => {
      var val = dataRow[colIdx];
      
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
- This is an official ECharts example from `matrix-mini-bar-geo/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
