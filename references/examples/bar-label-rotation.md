# 柱状图标签旋转 / Bar Label Rotation

**Category:** `bar`
**Example dir:** `bar-label-rotation`
**Difficulty:** 3

## Template Match
- **3d/bar3d.html** — Bar3D

## Option Code
```javascript
const posList = [
  'left',
  'right',
  'top',
  'bottom',
  'inside',
  'insideTop',
  'insideLeft',
  'insideRight',
  'insideBottom',
  'insideTopLeft',
  'insideTopRight',
  'insideBottomLeft',
  'insideBottomRight'
];
app.configParameters = {
  rotate: {
    min: -90,
    max: 90
  },
  align: {
    options: {
      left: 'left',
      center: 'center',
      right: 'right'
    }
  },
  verticalAlign: {
    options: {
      top: 'top',
      middle: 'middle',
      bottom: 'bottom'
    }
  },
  position: {
    options: posList.reduce(function (map, pos) {
      map[pos] = pos;
      return map;
    }, {})
  },
  distance: {
    min: 0,
    max: 100
  }
};
app.config = {
  rotate: 90,
  align: 'left',
  verticalAlign: 'middle',
  position: 'insideBottom',
  distance: 15,
  onChange: function () {
    const labelOption = {
      rotate: app.config.rotate,
      align: app.config.align,
      verticalAlign: app.config.verticalAlign,
      position: app.config.position,
      distance: app.config.distance
    };
    myChart.setOption({
      series: [
        {
          label: labelOption
        },
        {
          label: labelOption
        },
        {
          label: labelOption
        },
        {
          label: labelOption
        }
      ]
    });
  }
};
const labelOption = {
  show: true,
  position: app.config.position,
  distance: app.config.distance,
  align: app.config.align,
  verticalAlign: app.config.verticalAlign,
  rotate: app.config.rotate,
  formatter: '{c}  {name|{a}}',
  fontSize: 16,
  rich: {
    name: {}
  }
};
option = {
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {
    data: ['Forest', 'Steppe', 'Desert', 'Wetland']
  },
  toolbox: {
    show: true,
    orient: 'vertical',
    left: 'right',
    top: 'center',
    feature: {
      mark: { show: true },
      dataView: { show: true, readOnly: false },
      magicType: { show: true, type: ['line', 'bar', 'stack'] },
      restore: { show: true },
      saveAsImage: { show: true }
    }
  },
  xAxis: [
    {
      type: 'category',
      axisTick: { show: false },
      data: ['2012', '2013', '2014', '2015', '2016']
    }
  ],
  yAxis: [
    {
      type: 'value'
    }
  ],
  series: [
    {
      name: 'Forest',
      type: 'bar',
      barGap: 0,
      label: labelOption,
      emphasis: {
        focus: 'series'
      },
      data: [320, 332, 301, 334, 390]
    },
    {
      name: 'Steppe',
      type: 'bar',
      label: labelOption,
      emphasis: {
        focus: 'series'
      },
      data: [220, 182, 191, 234, 290]
    },
    {
      name: 'Desert',
      type: 'bar',
      label: labelOption,
      emphasis: {
        focus: 'series'
      },
      data: [150, 232, 201, 154, 190]
    },
    {
      name: 'Wetland',
      type: 'bar',
      label: labelOption,
      emphasis: {
        focus: 'series'
      },
      data: [98, 77, 101, 99, 40]
    }
  ]
};
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
- This is an official ECharts example from `bar-label-rotation/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
