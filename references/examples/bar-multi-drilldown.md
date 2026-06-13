# 柱状图多层下钻动画 / Bar Chart Multi-level Drilldown Animation

**Category:** `bar`
**Example dir:** `bar-multi-drilldown`
**Difficulty:** 6

## Template Match
- **3d/bar3d.html** — Bar3D

## Option Code
```javascript
// This example requires ECharts v5.5.0 or later
// level 1 (root)
const data_things = [
  ['Animals', 3, 'things', 'animals'],
  ['Fruits', 3, 'things', 'fruits'],
  ['Cars', 2, 'things', 'cars']
];
// level 2
const data_animals = [
  ['Dogs', 3, 'animals', 'dogs'],
  ['Cats', 4, 'animals', 'cats'],
  ['Birds', 3, 'animals', 'birds']
];
const data_fruits = [
  ['Pomes', 3, 'fruits', 'pomes'],
  ['Berries', 4, 'fruits', 'berries'],
  ['Citrus', 9, 'fruits', 'citrus']
];
const data_cars = [
  ['SUV', 5, 'cars', 'suv'],
  ['Sports', 3, 'cars', 'sports']
];
// level 3
const data_dogs = [
  ['Corgi', 5, 'dogs'],
  ['Bulldog', 6, 'dogs'],
  ['Shiba Inu', 7, 'dogs']
];
const data_cats = [
  ['American Shorthair', 2, 'cats'],
  ['British Shorthair', 9, 'cats'],
  ['Bengal', 2, 'cats'],
  ['Birman', 2, 'cats']
];
const data_birds = [
  ['Goose', 1, 'birds'],
  ['Owl', 2, 'birds'],
  ['Eagle', 8, 'birds']
];
const data_pomes = [
  ['Apple', 9, 'pomes'],
  ['Pear', 2, 'pomes'],
  ['Kiwi', 1, 'pomes']
];
const data_berries = [
  ['Blackberries', 7, 'berries'],
  ['Cranberries', 2, 'berries'],
  ['Strawberries', 9, 'berries'],
  ['Grapes', 4, 'berries']
];
const data_citrus = [
  ['Oranges', 3, 'citrus'],
  ['Grapefruits', 7, 'citrus'],
  ['Tangerines', 8, 'citrus'],
  ['Lemons', 7, 'citrus'],
  ['Limes', 3, 'citrus'],
  ['Kumquats', 2, 'citrus'],
  ['Citrons', 3, 'citrus'],
  ['Tengelows', 3, 'citrus'],
  ['Uglifruit', 1, 'citrus']
];
const data_suv = [
  ['Mazda CX-30', 7, 'suv'],
  ['BMW X2', 7, 'suv'],
  ['Ford Bronco Sport', 2, 'suv'],
  ['Toyota RAV4', 9, 'suv'],
  ['Porsche Macan', 4, 'suv']
];
const data_sports = [
  ['Porsche 718 Cayman', 2, 'sports'],
  ['Porsche 911 Turbo', 2, 'sports'],
  ['Ferrari F8', 4, 'sports']
];
const allLevelData = [
  data_things,
  data_animals,
  data_fruits,
  data_cars,
  data_dogs,
  data_cats,
  data_birds,
  data_pomes,
  data_berries,
  data_citrus,
  data_suv,
  data_sports
];
const allOptions = {};
allLevelData.forEach((data, index) => {
  // since dataItems of each data have same groupId in this
  // example, we can use groupId as optionId for optionStack.
  const optionId = data[0][2];
  const option = {
    id: optionId,
    xAxis: {
      type: 'category'
    },
    yAxis: {
      minInterval: 1
    },
    animationDurationUpdate: 500,
    series: {
      type: 'bar',
      dimensions: ['x', 'y', 'groupId', 'childGroupId'],
      encode: {
        x: 'x',
        y: 'y',
        itemGroupId: 'groupId',
        itemChildGroupId: 'childGroupId'
      },
      data,
      universalTransition: {
        enabled: true,
        divideShape: 'clone'
      }
    },
    graphic: [
      {
        type: 'text',
        left: 50,
        top: 20,
        style: {
          text: 'Back',
          fontSize: 18,
          fill: 'grey'
        },
        onclick: function () {
          goBack();
        }
      }
    ]
  };
  allOptions[optionId] = option;
});
// A stack to remember previous option id
const optionStack 
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
- This is an official ECharts example from `bar-multi-drilldown/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
