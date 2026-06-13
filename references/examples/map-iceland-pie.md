# 在地图上显示饼图 / Pie Charts on GEO Map

**Category:** `map, pie`
**Example dir:** `map-iceland-pie`
**Difficulty:** 5

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/geo/iceland.geo.json', function (geoJSON) {
  echarts.registerMap('iceland', geoJSON);
  function randomPieSeries(center, radius) {
    const data = ['A', 'B', 'C', 'D'].map((t) => {
      return {
        value: Math.round(Math.random() * 100),
        name: 'Category ' + t
      };
    });
    return {
      type: 'pie',
      coordinateSystem: 'geo',
      tooltip: {
        formatter: '{b}: {c} ({d}%)'
      },
      label: {
        show: false
      },
      labelLine: {
        show: false
      },
      animationDuration: 0,
      radius,
      center,
      data
    };
  }
  option = {
    geo: {
      map: 'iceland',
      roam: true,
      aspectScale: Math.cos((65 * Math.PI) / 180),
      // nameProperty: 'name_en', // If using en name.
      itemStyle: {
        areaColor: '#e7e8ea'
      },
      emphasis: {
        label: { show: false }
      }
    },
    tooltip: {},
    legend: {},
    series: [
      randomPieSeries([-19.007740346534653, 64.1780281585128], 45),
      randomPieSeries([-17.204666089108912, 65.44804833928391], 25),
      randomPieSeries([-15.264995297029705, 64.8592208009264], 30),
      randomPieSeries(
        // it's also supported to use geo region name as center since v5.4.1
        +echarts.version.split('.').slice(0, 3).join('') > 540
          ? 'Vestfirðir'
          : // or you can only use the LngLat array
            [-13, 66],
        30
      )
    ]
  };
  myChart.hideLoading();
  myChart.setOption(option);
});
```

## Relevant Debug Patterns
## #17
 — Pie 模板 roseType/RADIUS 类型错误导致空白
- **日期**：2026-06-13
- **现象**：09_Pie_Basic 空白，无任何图表
- **根因**：(1) `ROSE_TYPE: ""` → JS 中变成 `roseType: ''`（空字符串），ECharts 不接受空串，只接受 `false`/`'radius'`/`'area'`；(2) `RADIUS: "['40%','70%']"` 被 `_json_safe` 当作字符串处理，单引号 JSON 解析失败，输出为带转义的字符串而非数组
- **修复**：(1) `ROSE_TYPE: "false"` → `_json_safe` 识别为 JS keyword，输出 `false`；(2) `RADIUS` 改为 Python list `["40%","70%"]` → `_json_safe` 用 `json.dumps` 正确序列化为 JS 数组 `["40%","70%"]`；(3) **模板 `pie/basic.html` 增加防御**：`roseType` 默认为 `...

## #21
 — Sunburst 空白：RADIUS 字符串 + FOCUS 值非法
- **日期**：2026-06-13
- **现象**：20_Sunburst 一片空白
- **根因**：(1) `RADIUS: "['0%','90%']"` — 字符串假数组，同 #17 pie 的问题，`_json_safe` 将其当作字符串处理；(2) `FOCUS: "none"` — ECharts sunburst `emphasis.focus` 只接受 `'ancestor'` 或 `'descendant'`，不接受 `'none'`
- **修复**：(1) `RADIUS` 改为 `D(["0%","90%"])` — JSON 数组；(2) `FOCUS: "ancestor"`；(3) **模板增加防御**：`radius: {{RADIUS}} || ["0%","90%"]` 和 `focus: {{FOCUS}} || "ancestor"`

---
...

## Key Points
- This is an official ECharts example from `map-iceland-pie/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
