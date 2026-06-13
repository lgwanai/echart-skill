# 性能分析图 / Profile

**Category:** `custom`
**Example dir:** `custom-profile`
**Difficulty:** 3

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
var data = [];
var dataCount = 10;
var startTime = +new Date();
var categories = ['categoryA', 'categoryB', 'categoryC'];
var types = [
  { name: 'JS Heap', color: '#7b9ce1' },
  { name: 'Documents', color: '#bd6d6c' },
  { name: 'Nodes', color: '#75d874' },
  { name: 'Listeners', color: '#e0bc78' },
  { name: 'GPU Memory', color: '#dc77dc' },
  { name: 'GPU', color: '#72b362' }
];
// Generate mock data
categories.forEach(function (category, index) {
  var baseTime = startTime;
  for (var i = 0; i < dataCount; i++) {
    var typeItem = types[Math.round(Math.random() * (types.length - 1))];
    var duration = Math.round(Math.random() * 10000);
    data.push({
      name: typeItem.name,
      value: [index, baseTime, (baseTime += duration), duration],
      itemStyle: {
        normal: {
          color: typeItem.color
        }
      }
    });
    baseTime += Math.round(Math.random() * 2000);
  }
});
function renderItem(params, api) {
  var categoryIndex = api.value(0);
  var start = api.coord([api.value(1), categoryIndex]);
  var end = api.coord([api.value(2), categoryIndex]);
  var height = api.size([0, 1])[1] * 0.6;
  var rectShape = echarts.graphic.clipRectByRect(
    {
      x: start[0],
      y: start[1] - height / 2,
      width: end[0] - start[0],
      height: height
    },
    {
      x: params.coordSys.x,
      y: params.coordSys.y,
      width: params.coordSys.width,
      height: params.coordSys.height
    }
  );
  return (
    rectShape && {
      type: 'rect',
      transition: ['shape'],
      shape: rectShape,
      style: api.style()
    }
  );
}
option = {
  tooltip: {
    formatter: function (params) {
      return params.marker + params.name + ': ' + params.value[3] + ' ms';
    }
  },
  title: {
    text: 'Profile',
    left: 'center'
  },
  dataZoom: [
    {
      type: 'slider',
      filterMode: 'weakFilter',
      showDataShadow: false,
      top: 400,
      labelFormatter: ''
    },
    {
      type: 'inside',
      filterMode: 'weakFilter'
    }
  ],
  grid: {
    height: 300
  },
  xAxis: {
    min: startTime,
    scale: true,
    axisLabel: {
      formatter: function (val) {
        return Math.max(0, val - startTime) + ' ms';
      }
    }
  },
  yAxis: {
    data: categories
  },
  series: [
    {
      type: 'custom',
      renderItem: renderItem,
      itemStyle: {
        opacity: 0.8
      },
      encode: {
        x: [1, 2],
        y: 0
      },
      data: data
    }
  ]
};
```

## Relevant Debug Patterns
## #32
 — Error Bar 空白：custom renderItem 函数无法通过占位符传递
- **日期**：2026-06-13
- **现象**：39_Custom_Error_Bar 空白
- **根因**：(1) `RENDER_ITEM: "false"` → 无渲染函数，custom 类型不知道该画什么；(2) 多行 JS 函数无法通过 Python 字符串占位符传递（换行导致语法错误）
- **修复**：(1) `renderItem` 直接硬编码在模板中；(2) 模板简化为只需 `DATA` 占位符；(3) 误差线红色 `#e54035`，柱体蓝色 `#5470c6`

---
...

## Key Points
- This is an official ECharts example from `custom-profile/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
