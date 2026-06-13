# 水印 - ECharts 下载统计 / Watermark - ECharts Download

**Category:** `bar`
**Example dir:** `watermark`
**Difficulty:** 6

## Template Match
- **3d/bar3d.html** — Bar3D

## Option Code
```javascript
const builderJson = {
  all: 10887,
  charts: {
    map: 3237,
    lines: 2164,
    bar: 7561,
    line: 7778,
    pie: 7355,
    scatter: 2405,
    candlestick: 1842,
    radar: 2090,
    heatmap: 1762,
    treemap: 1593,
    graph: 2060,
    boxplot: 1537,
    parallel: 1908,
    gauge: 2107,
    funnel: 1692,
    sankey: 1568
  },
  components: {
    geo: 2788,
    title: 9575,
    legend: 9400,
    tooltip: 9466,
    grid: 9266,
    markPoint: 3419,
    markLine: 2984,
    timeline: 2739,
    dataZoom: 2744,
    visualMap: 2466,
    toolbox: 3034,
    polar: 1945
  },
  ie: 9743
};
const downloadJson = {
  'echarts.min.js': 17365,
  'echarts.simple.min.js': 4079,
  'echarts.common.min.js': 6929,
  'echarts.js': 14890
};
const themeJson = {
  'dark.js': 1594,
  'infographic.js': 925,
  'shine.js': 1608,
  'roma.js': 721,
  'macarons.js': 2179,
  'vintage.js': 1982
};
const waterMarkText = 'ECHARTS';
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
canvas.width = canvas.height = 100;
ctx.textAlign = 'center';
ctx.textBaseline = 'middle';
ctx.globalAlpha = 0.08;
ctx.font = '20px Microsoft Yahei';
ctx.translate(50, 50);
ctx.rotate(-Math.PI / 4);
ctx.fillText(waterMarkText, 0, 0);
option = {
  backgroundColor: {
    type: 'pattern',
    image: canvas,
    repeat: 'repeat'
  },
  tooltip: {},
  title: [
    {
      text: '在线构建',
      subtext: '总计 ' + builderJson.all,
      left: '25%',
      textAlign: 'center'
    },
    {
      text: '各版本下载',
      subtext:
        '总计 ' +
        Object.keys(downloadJson).reduce(function (all, key) {
          return all + downloadJson[key];
        }, 0),
      left: '75%',
      textAlign: 'center'
    },
    {
      text: '主题下载',
      subtext:
        '总计 ' +
        Object.keys(themeJson).reduce(function (all, key) {
          return all + themeJson[key];
        }, 0),
      left: '75%',
      top: '50%',
      textAlign: 'center'
    }
  ],
  grid: [
    {
      top: 50,
      width: '50%',
      bottom: '45%',
      left: 10,
      containLabel: true
    },
    {
      top: '55%',
      width: '50%',
      bottom: 0,
      left: 10,
      containLabel: true
    }
  ],
  xAxis: [
    {
      type: 'value',
      max: builderJson.all,
      splitLine: {
        show: false
      }
    },
    {
      type: 'value',
      max: builderJson.all,
      gridIndex: 1,
      splitLine: {
        show: false
      }
    }
  ],
  yAxis: [
    {
      type: 'category',
      data: Object.keys(builderJson.charts),
      axisLabel: {
        interval: 0,
        rotate: 30
      },
      splitLine: {
        show: false
      }
    },
    {
      gridIndex: 1,
      type: 'category',
      data: Object.keys(builderJson.components),
      axisLabel: {
        interval: 0,
        rotate: 30
      },
      splitLine: {
        show: false
      }
    }
  ],
  series: [
    {
      type: 'bar',
      stack: 'chart',
      z: 3,
      label: {
        position: 'right',
        show: t
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
- This is an official ECharts example from `watermark/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
