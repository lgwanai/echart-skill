# 交通（SVG） / GEO SVG Traffic

**Category:** `map`
**Example dir:** `geo-svg-traffic`
**Difficulty:** 

## Template Match
- **calendar/heatmap.html** — Calendar Heatmap

## Option Code
```javascript
$.get(ROOT_PATH + '/data/asset/geo/ksia-ext-plan-min.svg', function (svg) {
  echarts.registerMap('ksia-ext-plan', { svg: svg });
  option = {
    tooltip: {},
    geo: {
      map: 'ksia-ext-plan',
      roam: true,
      layoutCenter: ['50%', '50%'],
      layoutSize: '100%'
    },
    series: [
      {
        name: 'Route',
        type: 'lines',
        coordinateSystem: 'geo',
        geoIndex: 0,
        emphasis: {
          label: {
            show: false
          }
        },
        polyline: true,
        lineStyle: {
          color: '#c46e54',
          width: 0
        },
        effect: {
          show: true,
          period: 8,
          color: '#a10000',
          // constantSpeed: 80,
          trailLength: 0,
          symbolSize: [12, 30],
          symbol:
            'path://M87.1667 3.8333L80.5.5h-60l-6.6667 3.3333L.5 70.5v130l10 10h80l10 -10v-130zM15.5 190.5l15 -20h40l15 20zm75 -65l-15 5v35l15 15zm-80 0l15 5v35l-15 15zm65 0l15 -5v-40l-15 20zm-50 0l-15 -5v-40l15 20zm 65,-55 -15,25 c -15,-5 -35,-5 -50,0 l -15,-25 c 25,-15 55,-15 80,0 z'
        },
        z: 100,
        data: [
          {
            effect: {
              color: '#a10000',
              constantSpeed: 100,
              delay: 0
            },
            coords: [
              [50.875133928571415, 242.66287667410717],
              [62.03696428571425, 264.482421875],
              [72.63357421874997, 273.62779017857144],
              [92.78291852678569, 285.869140625],
              [113.43637834821425, 287.21854073660717],
              [141.44788783482142, 288.92947823660717],
              [191.71686104910714, 289.5507114955357],
              [198.3060072544643, 294.0673828125],
              [204.99699497767858, 304.60288783482144],
              [210.79177734375003, 316.7373046875],
              [212.45179408482142, 329.3656529017857],
              [210.8885267857143, 443.3925083705358],
              [215.35936941964286, 453.00634765625],
              [224.38761997767858, 452.15087890625],
              [265.71490792410714, 452.20179966517856],
              [493.3408844866072, 453.77525111607144],
              [572.8892940848216, 448.77992466517856],
              [608.9513755580358, 448.43366350446433],
              [619.99099609375, 450.8778599330358],
              [624.2479715401787, 456.2194475446429],
              [628.1434095982145, 463.9899553571429],
              [629.8492550223216, 476.0276227678571],
              [631.2750362723216, 535.7322126116071],
              [624.6757059151787, 546.6496233258929],
              [617.1801702008929, 552.6480887276786],
              [603.7269056919645, 554.5066964285714],
              [588.0178515625, 557.5517578125],
              [529.4386104910716, 556.2991071428571],
              [422.1994921875001, 551.38525390625],
              [291.66921875, 552.5767996651786],
              [219.4279380580357, 547.4949079241071],
              [209.53912667410714, 541.5931919642858],
  
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
- This is an official ECharts example from `geo-svg-traffic/main.js`
- Template data format: `[[dateString, value], ...]  (dateString: 'YYYY-MM-DD')`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
