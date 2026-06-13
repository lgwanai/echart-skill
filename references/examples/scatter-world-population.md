# World Population (2011) / World Population (2011)

**Category:** `scatter`
**Example dir:** `scatter-world-population`
**Difficulty:** 

## Template Match
- **3d/scatter3d.html** — Scatter3D

## Option Code
```javascript
var latlong = {};
latlong.AD = { latitude: 42.5, longitude: 1.5 };
latlong.AE = { latitude: 24, longitude: 54 };
latlong.AF = { latitude: 33, longitude: 65 };
latlong.AG = { latitude: 17.05, longitude: -61.8 };
latlong.AI = { latitude: 18.25, longitude: -63.1667 };
latlong.AL = { latitude: 41, longitude: 20 };
latlong.AM = { latitude: 40, longitude: 45 };
latlong.AN = { latitude: 12.25, longitude: -68.75 };
latlong.AO = { latitude: -12.5, longitude: 18.5 };
latlong.AP = { latitude: 35, longitude: 105 };
latlong.AQ = { latitude: -90, longitude: 0 };
latlong.AR = { latitude: -34, longitude: -64 };
latlong.AS = { latitude: -14.3333, longitude: -170 };
latlong.AT = { latitude: 47.3333, longitude: 13.3333 };
latlong.AU = { latitude: -27, longitude: 133 };
latlong.AW = { latitude: 12.5, longitude: -69.9667 };
latlong.AZ = { latitude: 40.5, longitude: 47.5 };
latlong.BA = { latitude: 44, longitude: 18 };
latlong.BB = { latitude: 13.1667, longitude: -59.5333 };
latlong.BD = { latitude: 24, longitude: 90 };
latlong.BE = { latitude: 50.8333, longitude: 4 };
latlong.BF = { latitude: 13, longitude: -2 };
latlong.BG = { latitude: 43, longitude: 25 };
latlong.BH = { latitude: 26, longitude: 50.55 };
latlong.BI = { latitude: -3.5, longitude: 30 };
latlong.BJ = { latitude: 9.5, longitude: 2.25 };
latlong.BM = { latitude: 32.3333, longitude: -64.75 };
latlong.BN = { latitude: 4.5, longitude: 114.6667 };
latlong.BO = { latitude: -17, longitude: -65 };
latlong.BR = { latitude: -10, longitude: -55 };
latlong.BS = { latitude: 24.25, longitude: -76 };
latlong.BT = { latitude: 27.5, longitude: 90.5 };
latlong.BV = { latitude: -54.4333, longitude: 3.4 };
latlong.BW = { latitude: -22, longitude: 24 };
latlong.BY = { latitude: 53, longitude: 28 };
latlong.BZ = { latitude: 17.25, longitude: -88.75 };
latlong.CA = { latitude: 54, longitude: -100 };
latlong.CC = { latitude: -12.5, longitude: 96.8333 };
latlong.CD = { latitude: 0, longitude: 25 };
latlong.CF = { latitude: 7, longitude: 21 };
latlong.CG = { latitude: -1, longitude: 15 };
latlong.CH = { latitude: 47, longitude: 8 };
latlong.CI = { latitude: 8, longitude: -5 };
latlong.CK = { latitude: -21.2333, longitude: -159.7667 };
latlong.CL = { latitude: -30, longitude: -71 };
latlong.CM = { latitude: 6, longitude: 12 };
latlong.CN = { latitude: 35, longitude: 105 };
latlong.CO = { latitude: 4, longitude: -72 };
latlong.CR = { latitude: 10, longitude: -84 };
latlong.CU = { latitude: 21.5, longitude: -80 };
latlong.CV = { latitude: 16, longitude: -24 };
latlong.CX = { latitude: -10.5, longitude: 105.6667 };
latlong.CY = { latitude: 35, longitude: 33 };
latlong.CZ = { latitude: 49.75, longitude: 15.5 };
latlong.DE = { latitude: 51, longitude: 9 };
latlong.DJ = { latitude: 11.5, longitude: 43 };
latlong.DK = { latitude: 56, longitude: 10 };
latlong.DM = { latitude: 15.4167, longitude: -61.3333 };
latlong.DO = { latitude: 19, longitude: -70.6667 };
latlong.DZ = { latitude: 28, longitude: 3 };
latlong.EC = { latitude: -2, longi
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
- This is an official ECharts example from `scatter-world-population/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
