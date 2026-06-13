# 极坐标系下的柱状图 / Bar Chart on Polar

**Category:** `bar`
**Example dir:** `bar-polar-real-estate`
**Difficulty:** 7

## Template Match
- **3d/bar3d.html** — Bar3D

## Option Code
```javascript
const data = [
  [5000, 10000, 6785.71],
  [4000, 10000, 6825],
  [3000, 6500, 4463.33],
  [2500, 5600, 3793.83],
  [2000, 4000, 3060],
  [2000, 4000, 3222.33],
  [2500, 4000, 3133.33],
  [1800, 4000, 3100],
  [2000, 3500, 2750],
  [2000, 3000, 2500],
  [1800, 3000, 2433.33],
  [2000, 2700, 2375],
  [1500, 2800, 2150],
  [1500, 2300, 2100],
  [1600, 3500, 2057.14],
  [1500, 2600, 2037.5],
  [1500, 2417.54, 1905.85],
  [1500, 2000, 1775],
  [1500, 1800, 1650]
];
// prettier-ignore
const cities = ['北京', '上海', '深圳', '广州', '苏州', '杭州', '南京', '福州', '青岛', '济南', '长春', '大连', '温州', '郑州', '武汉', '成都', '东莞', '沈阳', '烟台'];
const barHeight = 50;
option = {
  title: {
    text: 'How expensive is it to rent an apartment in China?',
    subtext: 'Data from https://www.numbeo.com'
  },
  legend: {
    show: true,
    top: 'bottom',
    data: ['Range', 'Average']
  },
  grid: {
    top: 100
  },
  angleAxis: {
    type: 'category',
    data: cities
  },
  tooltip: {
    show: true,
    formatter: function (params) {
      const id = params.dataIndex;
      return (
        cities[id] +
        '<br>Lowest：' +
        data[id][0] +
        '<br>Highest：' +
        data[id][1] +
        '<br>Average：' +
        data[id][2]
      );
    }
  },
  radiusAxis: {},
  polar: {},
  series: [
    {
      type: 'bar',
      itemStyle: {
        color: 'transparent'
      },
      data: data.map(function (d) {
        return d[0];
      }),
      coordinateSystem: 'polar',
      stack: 'Min Max',
      silent: true
    },
    {
      type: 'bar',
      data: data.map(function (d) {
        return d[1] - d[0];
      }),
      coordinateSystem: 'polar',
      name: 'Range',
      stack: 'Min Max'
    },
    {
      type: 'bar',
      itemStyle: {
        color: 'transparent'
      },
      data: data.map(function (d) {
        return d[2] - barHeight;
      }),
      coordinateSystem: 'polar',
      stack: 'Average',
      silent: true,
      z: 10
    },
    {
      type: 'bar',
      data: data.map(function (d) {
        return barHeight * 2;
      }),
      coordinateSystem: 'polar',
      name: 'Average',
      stack: 'Average',
      barGap: '-100%',
      z: 10
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
- This is an official ECharts example from `bar-polar-real-estate/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
