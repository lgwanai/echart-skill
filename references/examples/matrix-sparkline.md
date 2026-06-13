# 矩阵中的微型折线图 / Mini Line Charts (Sparkline) in Matrix

**Category:** `matrix, line`
**Example dir:** `matrix-sparkline`
**Difficulty:** 5

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
const _matrixDimensionData = {
  x: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
  y: [
    { value: '8:00\n~\n10:00' },
    { value: '10:00\n~\n12:00' },
    { value: '12:00\n~\n14:00', size: 55 },
    { value: '14:00\n~\n16:00' },
    { value: '16:00\n~\n18:00' },
    { value: '18:00\n~\n20:00' }
  ]
};
const _yBreakTimeIndex = 2; // '12:00 - 14:00',
const _seriesFakeDataLength = 365;
option = {
  matrix: {
    x: {
      data: _matrixDimensionData.x,
      levelSize: 40,
      label: {
        fontSize: 16,
        color: '#555'
      }
    },
    y: {
      data: _matrixDimensionData.y,
      levelSize: 70,
      label: {
        fontSize: 14,
        color: '#777'
      }
    },
    corner: {
      data: [
        {
          coord: [-1, -1],
          value: 'Time'
        }
      ],
      label: {
        fontSize: 16,
        color: '#777'
      }
    },
    body: {
      data: [
        {
          coord: [null, _yBreakTimeIndex],
          coordClamp: true,
          mergeCells: true,
          value: 'Break',
          label: {
            color: '#999',
            fontSize: 16
          }
        }
      ]
    },
    top: 30,
    bottom: 80,
    width: '90%',
    left: 'center'
  },
  tooltip: {
    trigger: 'axis'
  },
  dataZoom: [
    {
      type: 'slider',
      xAxisIndex: 'all',
      left: '10%',
      right: '10%',
      bottom: 30,
      height: 30,
      throttle: 120
    },
    {
      type: 'inside',
      xAxisIndex: 'all',
      throttle: 120
    }
  ],
  grid: [],
  xAxis: [],
  yAxis: [],
  series: []
};
eachMatrixCell((xval, yval, xidx, yidx) => {
  const id = makeId(xidx, yidx);
  option.grid.push({
    id: id,
    coordinateSystem: 'matrix',
    coord: [xval, yval],
    top: 10,
    bottom: 10,
    left: 'center',
    width: '90%',
    containLabel: true
  });
  option.xAxis.push({
    type: 'category',
    id: id,
    gridId: id,
    scale: true,
    axisTick: { show: false },
    axisLabel: { show: false },
    axisLine: { show: false },
    splitLine: { show: false }
  });
  option.yAxis.push({
    id: id,
    gridId: id,
    interval: Number.MAX_SAFE_INTEGER,
    scale: true,
    axisLabel: {
      showMaxLabel: true,
      fontSize: 9
    },
    axisLine: { show: false },
    axisTick: { show: false }
  });
  option.series.push({
    xAxisId: id,
    yAxisId: id,
    type: 'line',
    symbol: 'none',
    lineStyle: {
      lineWidth: 1
    },
    data: generateFakeSeriesData(_seriesFakeDataLength, xidx, yidx)
  });
});
// ------ Helpers Start ------
function makeId(xidx, yidx) {
  return `${xidx}|${yidx}`;
}
function eachMatrixCell(cb) {
  _matrixDimensionData.y.forEach((yvalItem, yidx) => {
    const yval = yvalItem.value;
    if (yidx === _yBreakTimeIndex) {
      return;
    }
    _matrixDimensionData.x.forEach((xval, xidx) => {
      cb(xval, yval, xidx, yidx);
    });
  });
}
function generateFakeSeriesData(dayCount, xidx, yidx) {
  const dayStart = new Date('2025-05-05T00:00:00.000Z'); // Monday
  dayStart.setD
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
- This is an official ECharts example from `matrix-sparkline/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
