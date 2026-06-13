# 折线图鱼眼放大 / Fisheye Lens on Line Chart

**Category:** `line`
**Example dir:** `line-fisheye-lens`
**Difficulty:** 8

## Template Match
- **3d/lines3d.html** — Lines3D

## Option Code
```javascript
var GRID_TOP = 120;
var GRID_BOTTOM = 80;
var GRID_LEFT = 60;
var GRID_RIGHT = 60;
var Y_DATA_ROUND_PRECISION = 0;
var _breakAreaStyle = {
  expandOnClick: false,
  zigzagZ: 200,
  zigzagAmplitude: 0,
  itemStyle: {
    borderColor: '#777',
    opacity: 0
  }
};
option = {
  title: {
    text: 'Fisheye Lens on Line Chart',
    subtext: 'Brush to magnify the details',
    left: 'center',
    textStyle: {
      fontSize: 20
    },
    subtextStyle: {
      color: '#175ce5',
      fontSize: 15,
      fontWeight: 'bold'
    }
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {},
  grid: {
    top: GRID_TOP,
    bottom: GRID_BOTTOM,
    left: GRID_LEFT,
    right: GRID_RIGHT
  },
  xAxis: [
    {
      splitLine: {
        show: false
      },
      breakArea: _breakAreaStyle
    }
  ],
  yAxis: [
    {
      axisTick: {
        show: true
      },
      breakArea: _breakAreaStyle
    }
  ],
  series: [
    {
      type: 'line',
      name: 'Data A',
      symbol: 'circle',
      showSymbol: false,
      symbolSize: 5,
      data: generateSeriesData()
    }
  ]
};

function initAxisBreakInteraction() {
  var _brushingEl = null;
  myChart.on('click', function (params) {
    if (params.name === 'clearAxisBreakBtn') {
      var option = {
        xAxis: { breaks: [] },
        yAxis: { breaks: [] }
      };
      addClearButtonUpdateOption(option, false);
      myChart.setOption(option);
    }
  });
  function addClearButtonUpdateOption(option, show) {
    option.graphic = [
      {
        elements: [
          {
            type: 'rect',
            ignore: !show,
            name: 'clearAxisBreakBtn',
            top: 5,
            left: 5,
            shape: { r: 3, width: 70, height: 30 },
            style: { fill: '#eee', stroke: '#999', lineWidth: 1 },
            textContent: {
              type: 'text',
              style: {
                text: 'Reset',
                fontSize: 15,
                fontWeight: 'bold'
              }
            },
            textConfig: { position: 'inside' }
          }
        ]
      }
    ];
  }
  myChart.getZr().on('mousedown', function (params) {
    _brushingEl = new echarts.graphic.Rect({
      shape: { x: params.offsetX, y: params.offsetY },
      style: { stroke: 'none', fill: '#ccc' },
      ignore: true
    });
    myChart.getZr().add(_brushingEl);
  });
  myChart.getZr().on('mousemove', function (params) {
    if (!_brushingEl) {
      return;
    }
    var initX = _brushingEl.shape.x;
    var initY = _brushingEl.shape.y;
    var currPoint = [params.offsetX, params.offsetY];
    _brushingEl.setShape('width', currPoint[0] - initX);
    _brushingEl.setShape('height', currPoint[1] - initY);
    _brushingEl.ignore = false;
  });
  document.addEventListener('mouseup', function (params) {
    if (!_brushingEl) {
      return;
    }
    var initX = _brushingEl.shape.x;
    var initY = _brushingEl.shape.y;
    var currPoint = [params.offsetX, params.offsetY];
    var xPixelSpan = Math.abs(currPoin
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
- This is an official ECharts example from `line-fisheye-lens/main.js`
- Template data format: `{ geoCoordMap: {"name": [lng, lat]}, flights: [[fromName, toName], ...] }`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
