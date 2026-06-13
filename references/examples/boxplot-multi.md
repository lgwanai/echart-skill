# 多系列盒须图 / Multiple Categories

**Category:** `boxplot`
**Example dir:** `boxplot-multi`
**Difficulty:** 

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
// Generate data.
function makeData() {
  let data = [];
  for (let i = 0; i < 18; i++) {
    let cate = [];
    for (let j = 0; j < 100; j++) {
      cate.push(Math.random() * 200);
    }
    data.push(cate);
  }
  return data;
}
const data0 = makeData();
const data1 = makeData();
const data2 = makeData();
option = {
  title: {
    text: 'Multiple Categories',
    left: 'center'
  },
  dataset: [
    {
      source: data0
    },
    {
      source: data1
    },
    {
      source: data2
    },
    {
      fromDatasetIndex: 0,
      transform: { type: 'boxplot' }
    },
    {
      fromDatasetIndex: 1,
      transform: { type: 'boxplot' }
    },
    {
      fromDatasetIndex: 2,
      transform: { type: 'boxplot' }
    }
  ],
  legend: {
    top: '10%'
  },
  tooltip: {
    trigger: 'item',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '10%',
    top: '20%',
    right: '10%',
    bottom: '15%'
  },
  xAxis: {
    type: 'category',
    boundaryGap: true,
    nameGap: 30,
    splitArea: {
      show: true
    },
    splitLine: {
      show: false
    }
  },
  yAxis: {
    type: 'value',
    name: 'Value',
    min: -400,
    max: 600,
    splitArea: {
      show: false
    }
  },
  dataZoom: [
    {
      type: 'inside',
      start: 0,
      end: 20
    },
    {
      show: true,
      type: 'slider',
      top: '90%',
      xAxisIndex: [0],
      start: 0,
      end: 20
    }
  ],
  series: [
    {
      name: 'category0',
      type: 'boxplot',
      datasetIndex: 3
    },
    {
      name: 'category1',
      type: 'boxplot',
      datasetIndex: 4
    },
    {
      name: 'category2',
      type: 'boxplot',
      datasetIndex: 5
    }
  ]
};
```

## Relevant Debug Patterns
## #23
 — Boxplot 空白：依赖缺失的 ecStat 库
- **日期**：2026-06-13
- **现象**：24_Boxplot 一片空白
- **根因**：原模板使用 ECharts `transform: { type: 'boxplot' }`，需要 `ecStat` 扩展库，但项目中不存在该库
- **修复**：(1) 模板重写为预计算五数概括格式 `series.data: [[min, Q1, median, Q3, max], ...]`，无需 ecStat；(2) 数据从原始值改为 `[[740,880,935,980,1070],[800,860,900,940,960]]`

---
...

## Key Points
- This is an official ECharts example from `boxplot-multi/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
