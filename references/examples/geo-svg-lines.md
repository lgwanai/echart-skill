# GEO 路径图（SVG） / GEO SVG Lines

**Category:** `map`
**Example dir:** `geo-svg-lines`
**Difficulty:** 

## Template Match
- **calendar/heatmap.html** — Calendar Heatmap

## Option Code
```javascript
$.get(
  ROOT_PATH + '/data/asset/geo/MacOdrum-LV5-floorplan-web.svg',
  function (svg) {
    echarts.registerMap('MacOdrum-LV5-floorplan-web', { svg: svg });
    option = {
      title: {
        text: 'Visit Route',
        left: 'center',
        bottom: 10
      },
      tooltip: {},
      geo: {
        map: 'MacOdrum-LV5-floorplan-web',
        roam: true,
        emphasis: {
          itemStyle: {
            color: undefined
          },
          label: {
            show: false
          }
        }
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
            width: 5,
            opacity: 1,
            type: 'dotted'
          },
          effect: {
            show: true,
            period: 8,
            color: '#a10000',
            constantSpeed: 80,
            trailLength: 0,
            symbolSize: [20, 12],
            symbol:
              'path://M35.5 40.5c0-22.16 17.84-40 40-40s40 17.84 40 40c0 1.6939-.1042 3.3626-.3067 5H35.8067c-.2025-1.6374-.3067-3.3061-.3067-5zm90.9621-2.6663c-.62-1.4856-.9621-3.1182-.9621-4.8337 0-6.925 5.575-12.5 12.5-12.5s12.5 5.575 12.5 12.5a12.685 12.685 0 0 1-.1529 1.9691l.9537.5506-15.6454 27.0986-.1554-.0897V65.5h-28.7285c-7.318 9.1548-18.587 15-31.2715 15s-23.9535-5.8452-31.2715-15H15.5v-2.8059l-.0937.0437-8.8727-19.0274C2.912 41.5258.5 37.5549.5 33c0-6.925 5.575-12.5 12.5-12.5S25.5 26.075 25.5 33c0 .9035-.0949 1.784-.2753 2.6321L29.8262 45.5h92.2098z'
          },
          data: [
            {
              coords: [
                [110.6189462165178, 456.64349563895087],
                [124.10988522879458, 450.8570048730469],
                [123.9272226116071, 389.9520693708147],
                [61.58708083147317, 386.87942320312504],
                [61.58708083147317, 72.8954315876116],
                [258.29514854771196, 72.8954315876116],
                [260.75457021484374, 336.8559607533482],
                [280.5277985253906, 410.2406672084263],
                [275.948185765904, 528.0254369698661],
                [111.06907909458701, 552.795792593471],
                [118.87138231445309, 701.365737015904],
                [221.36468155133926, 758.7870354617745],
                [307.86195445452006, 742.164737297712],
                [366.8489324762834, 560.9895157073103],
                [492.8750778390066, 560.9895157073103],
                [492.8750778390066, 827.9639780566406],
                [294.9255269587053, 827.9639780566406],
                [282.79803391043527, 868.2476088113839]
              ]
            }
          ]
        }
      ]
    };
    myChart.setOption(option);
  }
);
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
- This is an official ECharts example from `geo-svg-lines/main.js`
- Template data format: `[[dateString, value], ...]  (dateString: 'YYYY-MM-DD')`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
