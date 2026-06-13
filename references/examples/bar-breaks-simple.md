# 断轴上的柱状图 / Bar Chart with Axis Breaks

**Category:** `bar`
**Example dir:** `bar-breaks-simple`
**Difficulty:** 3

## Template Match
- **3d/bar3d.html** — Bar3D

## Option Code
```javascript
var _currentAxisBreaks = [
  {
    start: 5000,
    end: 100000,
    gap: '1.5%'
  },
  {
    // `start` and `end` are also used as the identifier for a certain axis break.
    start: 105000,
    end: 3100000,
    gap: '1.5%'
  }
];
option = {
  title: {
    text: 'Bar Chart with Axis Breaks',
    subtext: 'Click the break area to expand it',
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
    top: 120
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
      data: [3106212, 3102118, 3102643, 3104631, 3106679, 3100130, 3107022],
      emphasis: {
        focus: 'series'
      }
    }
  ]
};

function initAxisBreakInteraction() {
  myChart.on('axisbreakchanged', function (params) {
    updateCollapseButton(params);
  });
  myChart.on('click', function (params) {
    if (params.name === 'collapseAxisBreakBtn') {
      collapseAxisBreak();
    }
  });
  function updateCollapseButton(params) {
    // If there is any axis break expanded, we need to show the collapse button.
    var needReset = false;
    for (let i = 0; i < params.breaks.length; i++) {
      const changedBreakItem = params.breaks[i];
      if (changedBreakItem.isExpanded) {
        needReset = true;
        break;
      }
    }
    myChart.setOption({
      // Draw the collapse button.
      graphic: [
        {
          elements: [
            {
              type: 'rect',
              ignore: !needReset,
              name: 'collapseAxisBreakBtn',
              top: 5,
              left: 5,
              shape: { r: 3, width: 140, height: 24 },
              style: { fill: '#eee', stroke: '#999', lineWidth: 1 },
              textContent: {
                type: 'text',
                style: {
                  text: 'Collapse Axis Breaks',
                  fontSize: 13,
                  fontWeight: 'bold'
                }
              },
              textConfig: { position: 'inside' }
            }
          ]
        }
      ]
    });
  }
  function collapseAxisBre
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
- This is an official ECharts example from `bar-breaks-simple/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
