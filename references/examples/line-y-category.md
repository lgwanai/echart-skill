# 垂直折线图（Y轴为类目轴） / Line Y Category

**Category:** `line`
**Example dir:** `line-y-category`
**Difficulty:** 8

## Template Match
- **3d/lines3d.html** — Lines3D

## Option Code
```javascript
option = {
  legend: {
    data: ['Altitude (km) vs. temperature (°C)']
  },
  tooltip: {
    trigger: 'axis',
    formatter: 'Temperature : <br/>{b}km : {c}°C'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    axisLabel: {
      formatter: '{value} °C'
    }
  },
  yAxis: {
    type: 'category',
    axisLine: { onZero: false },
    axisLabel: {
      formatter: '{value} km'
    },
    boundaryGap: false,
    data: ['0', '10', '20', '30', '40', '50', '60', '70', '80']
  },
  series: [
    {
      name: 'Altitude (km) vs. temperature (°C)',
      type: 'line',
      symbolSize: 10,
      symbol: 'circle',
      smooth: true,
      lineStyle: {
        width: 3,
        shadowColor: 'rgba(0,0,0,0.3)',
        shadowBlur: 10,
        shadowOffsetY: 8
      },
      data: [15, -50, -56.5, -46.5, -22.1, -2.5, -27.7, -55.7, -76.5]
    }
  ]
};
```

## Relevant Debug Patterns
## #14
 — Line XY 数据未排序导致折线锯齿
- **日期**：2026-06-13
- **现象**：08_Line_XY 折线来回穿梭，线条混乱
- **根因**：XY 折线图数据 `[[x,y],...]` 中 x 值未排序。ECharts line chart 按数组顺序连接点，不按 x 值排序
- **修复**：(1) 数据按 x 排序；(2) **模板 `line/xy.html` 新增 `data.sort()` 自动排序**，确保无论输入数据是否有序都能正确渲染

---
...

## #16
 — Stacked bar/line 模板 series 缺少 type 字段
- **日期**：2026-06-13
- **现象**：03_Bar_Stacked、07_Line_Stacked 无数据
- **根因**：`bar/stack.html` 和 `line/stack.html` 使用 `{{SERIES}}` 替换整个 series 数组，每个 series 对象必须带 `type: "bar"/"line"`。ECharts 没有默认 series type
- **修复**：数据 dict 中 series 对象添加 `"type": "bar"` 或 `"type": "line"`

---
...

## #18
 — Scatter Geo/Map 空白：MAP_INLINE 被替换导致地图未加载
- **日期**：2026-06-13
- **现象**：12_Scatter_Geo、13_Map_China 等地图类图表空白
- **根因**：数据 dict 中 `"MAP_INLINE": ""` → `_json_safe` 替换 `{{MAP_INLINE}}` 为 `''` → `<!-- {{MAP_INLINE}} -->` 变成 `<!-- '' -->` → `build_template.py` 的地图注入检测 `if "<!-- {{MAP_INLINE}} -->" in html` 失败 → China GeoJSON 未嵌入 → 地图空白
- **修复**：**不要在数据 dict 中提供 `MAP_INLINE`/`GL_INLINE`/`ECHARTS_INLINE` 这三个特殊占位符**。它们由 `build_template.py` 自动处理（代码中已排除此三类占位符的校验）。**模板不需要修改**——模板中的 `<!-- {{MAP_INLINE}} --...

## Key Points
- This is an official ECharts example from `line-y-category/main.js`
- Template data format: `{ geoCoordMap: {"name": [lng, lat]}, flights: [[fromName, toName], ...] }`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
