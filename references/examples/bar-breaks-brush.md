# 断轴上的柱状图（可刷选） / Bar Chart with Axis Breaks (Brush-enabled)

**Category:** `bar`
**Example dir:** `bar-breaks-brush`
**Difficulty:** 8

## Template Match
- **3d/bar3d.html** — Bar3D

## Option Code
```javascript
var GRID_TOP = 120;
var GRID_BOTTOM = 80;
var Y_DATA_ROUND_PRECISION = 0;
var _currentAxisBreaks = [
  {
    start: 5000,
    end: 100000,
    gap: '2%'
  }
];
option = {
  title: {
    text: 'Bar Chart with Axis Break (Brush-enabled)',
    subtext:
      'Brush to create a new axis break.\nClick on the break area to reset.',
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
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {},
  grid: {
    top: GRID_TOP,
    bottom: GRID_BOTTOM
  },
  xAxis: [
    {
      type: 'category',
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    }
  ],
  yAxis: [
    {
      type: 'value',
      breaks: _currentAxisBreaks,
      breakArea: {
        itemStyle: {
          opacity: 1
        },
        zigzagMaxSpan: 15,
        zigzagAmplitude: 2,
        zigzagZ: 200
      }
    }
  ],
  series: [
    {
      name: 'Data A',
      type: 'bar',
      emphasis: {
        focus: 'series'
      },
      data: [1500, 2032, 2001, 3154, 2190, 4330, 2410]
    },
    {
      name: 'Data B',
      type: 'bar',
      emphasis: {
        focus: 'series'
      },
      data: [1200, 1320, 1010, 1340, 900, 2300, 2100]
    },
    {
      name: 'Data C',
      type: 'bar',
      emphasis: {
        focus: 'series'
      },
      data: [103200, 100320, 103010, 102340, 103900, 103300, 103200]
    },
    {
      name: 'Data D',
      type: 'bar',
      data: [106212, 102118, 102643, 104631, 106679, 100130, 107022],
      emphasis: {
        focus: 'series'
      }
    }
  ]
};

function initAxisBreakInteraction() {
  var _brushingEl = null;
  myChart.getZr().on('mousedown', function (params) {
    _brushingEl = new echarts.graphic.Rect({
      shape: { x: 0, y: params.offsetY },
      style: { stroke: 'none', fill: '#ccc' },
      ignore: true
    });
    myChart.getZr().add(_brushingEl);
  });
  myChart.getZr().on('mousemove', function (params) {
    if (!_brushingEl) {
      return;
    }
    var initY = _brushingEl.shape.y;
    var currPoint = [params.offsetX, params.offsetY];
    _brushingEl.setShape('width', myChart.getWidth());
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
    var pixelSpan = Math.abs(currPoint[1] - initY);
    if (pixelSpan > 2) {
      updateAxisBreak(myChart, [initX, initY], currPoint);
    }
    myChart.getZr().remove(_brushingEl);
    _brushingEl = null;
  });
  myChart.on('axisbreakchanged', function (params) {
    // Remove expanded axis breaks from _currentAxisBreaks.
    var changedBreaks = params.breaks || [];
    for (var i = 0; i < changedBreaks.length; i+
```

## Relevant Debug Patterns
## #16
 — Stacked bar/line 模板 series 缺少 type 字段
- **日期**：2026-06-13
- **现象**：03_Bar_Stacked、07_Line_Stacked 无数据
- **根因**：`bar/stack.html` 和 `line/stack.html` 使用 `{{SERIES}}` 替换整个 series 数组，每个 series 对象必须带 `type: "bar"/"line"`。ECharts 没有默认 series type
- **修复**：数据 dict 中 series 对象添加 `"type": "bar"` 或 `"type": "line"`

---
...

## #24
 — PictorialBar：symbol 必须用真实位图，SVG/矢量路径效果差
- **日期**：2026-06-13
- **现象**：28_PictorialBar 显示纯色方块，无象形效果
- **根因**：(1) `SYMBOL: "rect"` → 普通矩形，不"象形"；(2) SVG 手绘路径质量差；(3) `SYMBOL_BOUNDING: "false"` → 无 bounding，所有值显为单个图标
- **修复**：(1) 下载 Twitter emoji CDN 的 72x72 PNG 光栅图（大象/犀牛/河马/水牛/长颈鹿）；(2) 通过 `data[i].symbol` 为每个数据项设置独立图标 URI；`symbolBoundingData: 1000`，`symbolRepeat: true`；(3) **模板增加防御**：`symbol` 为空时允许 data[i].symbol 覆盖

---
...

## #27
 — 3D Bar 空白：GL_INLINE + coordinateSystem + zAxis3D 配置错误
- **日期**：2026-06-13
- **现象**：33_3D_Bar 一片空白
- **根因**：(1) `GL_INLINE: ""` 破坏 echarts-gl 注入（同 #18）；(2) `coordinateSystem: 'cartesian3D'` + `zAxis3D: {type:'value'}` + `shading:'realistic'` 不是官方推荐的配置组合；(3) 官方示例用 `zAxis3D: {}`（空对象）、无 `coordinateSystem`、`shading: 'lambert'`
- **修复**：模板改为与 ECharts 官方 bar3D 示例完全一致的配置：`grid3D: {}`、`zAxis3D: {}`、`shading: 'lambert'`、无 `coordinateSystem`、无 `barSize`

---
...

## Key Points
- This is an official ECharts example from `bar-breaks-brush/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
