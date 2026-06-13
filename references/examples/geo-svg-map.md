# 地图（SVG） / GEO SVG Map

**Category:** `map`
**Example dir:** `geo-svg-map`
**Difficulty:** 

## Template Match
- **calendar/heatmap.html** — Calendar Heatmap

## Option Code
```javascript
$.get(
  ROOT_PATH + '/data/asset/geo/Sicily_prehellenic_topographic_map.svg',
  function (svg) {
    echarts.registerMap('sicily', { svg: svg });
    option = {
      tooltip: {
        formatter: function (params) {
          console.log(params);
          return [
            params.name + ':',
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx'
          ].join('<br>');
        }
      },
      geo: [
        {
          map: 'sicily',
          roam: true,
          layoutCenter: ['50%', '50%'],
          layoutSize: '100%',
          selectedMode: 'single',
          tooltip: {
            show: true,
            confine: true,
            formatter: function (params) {
              return [
                'This is the introduction:',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx'
              ].join('<br>');
            }
          },
          itemStyle: {
            color: undefined
          },
          emphasis: {
            label: {
              show: false
            }
          },
          select: {
            itemStyle: {
              color: '#b50205'
            },
            label: {
              show: false
            }
          },
          regions: [
            {
              name: 'route1',
              itemStyle: {
                borderWidth: 0
              },
              select: {
                itemStyle: {
                  color: '#b5280d',
                  borderWidth: 0
                }
              },
              tooltip: {
                position: 'right',
                alwaysShowContent: true,
                enterable: true,
                extraCssText: 'user-select: text',
                formatter: [
                  'Route 1:',
                  'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
                  'xxxxxxxxxxxxxxxxxxxxxxxxxxx'
                ].join('<br>')
              }
            },
            {
              name: 'route2',
              itemStyle: {
                borderWidth: 0
              },
              select: {
                itemStyle: {
                  color: '#b5280d',
                  borderWidth: 0
                }
              },
              tooltip: {
                position: 'left',
                alwaysShowContent: true,
                enterable: true,
                extraCssText: 'user-select: text',
                formatter: [
                  'Route 2:',
                  'xxxxxxxxxxxxxx',
          
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
- This is an official ECharts example from `geo-svg-map/main.js`
- Template data format: `[[dateString, value], ...]  (dateString: 'YYYY-MM-DD')`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
