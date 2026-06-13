# 地理坐标系上的等值区划图和散点图 / Geo Choropleth and Scatter

**Category:** `map, scatter`
**Example dir:** `geo-choropleth-scatter`
**Difficulty:** 5

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
function createChart() {
  var icelandRoughLatitude = 65;
  option = {
    geo: {
      map: 'iceland',
      roam: true,
      aspectScale: Math.cos((icelandRoughLatitude * Math.PI) / 180),
      // nameProperty: 'name_en', // If using en name.
      label: {
        show: true,
        color: '#555'
      }
    },
    tooltip: {},
    visualMap: [
      {
        orient: 'horizontal',
        calculable: true,
        right: 0,
        bottom: 0,
        seriesIndex: 0,
        // min/max is specified as series.data value extent.
        min: 0,
        max: 1e5,
        dimension: 2,
        inRange: {
          symbolSize: [5, 30]
        },
        controller: {
          inRange: {
            color: ['#66c2a5']
          }
        }
      },
      {
        orient: 'horizontal',
        calculable: true,
        left: 0,
        bottom: 0,
        seriesIndex: 1,
        // min/max is specified as series.data value extent.
        min: 0,
        max: 1e3,
        dimension: 0,
        inRange: {
          color: ['#deebf7', '#3182bd']
        }
      }
    ],
    series: [
      {
        type: 'scatter',
        coordinateSystem: 'geo',
        geoIndex: 0,
        encode: {
          // `2` is the dimension index of series.data
          tooltip: 2,
          label: 2
        },
        data: [
          [-21.9348415, 64.1334671, 14523],
          [-19.028531, 63.710241, 45126],
          [-17.089925, 65.37887072, 12345],
          [-19.15936, 65.6218101, 56789],
          [-19.849175, 65.7287035, 67890],
          [-23.18326, 65.582939, 89012],
          [-14.9515, 64.475135, 34567],
          [-20.88389, 63.85321, 45678]
        ],
        itemStyle: {
          color: '#66c2a5',
          borderWidth: 1,
          borderColor: '#3c7865'
        }
      },
      {
        // Effectively this is a choropleth map.
        type: 'map',
        // Specify geoIndex to share the geo component with the scatter series above,
        // instead of creating an internal geo coord sys.
        geoIndex: 0,
        map: '',
        data: [
          { name: 'Austurland', value: 423 },
          { name: 'Suðurland', value: 256 },
          { name: 'Norðurland vestra', value: 489 },
          { name: 'Norðurland eystra', value: 51 }
        ]
      }
    ]
  };
  myChart.setOption(option);
}
function fetchGeoJSON() {
  myChart.showLoading();
  $.get(ROOT_PATH + '/data/asset/geo/iceland.geo.json', function (geoJSON) {
    echarts.registerMap('iceland', geoJSON);
    createChart();
    myChart.hideLoading();
  });
}
fetchGeoJSON();
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
- This is an official ECharts example from `geo-choropleth-scatter/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
