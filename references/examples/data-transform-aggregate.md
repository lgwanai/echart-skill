# 简单的数据聚合 / Data Transform Simple Aggregate

**Category:** `boxplot`
**Example dir:** `data-transform-aggregate`
**Difficulty:** 4

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
$.when(
  $.get(ROOT_PATH + '/data/asset/data/life-expectancy-table.json'),
  $.getScript(
    CDN_PATH + 'echarts-simple-transform/dist/ecSimpleTransform.min.js'
  )
).done(function (res) {
  run(res[0]);
});
function run(_rawData) {
  echarts.registerTransform(ecSimpleTransform.aggregate);
  option = {
    dataset: [
      {
        id: 'raw',
        source: _rawData
      },
      {
        id: 'since_year',
        fromDatasetId: 'raw',
        transform: [
          {
            type: 'filter',
            config: {
              dimension: 'Year',
              gte: 1950
            }
          }
        ]
      },
      {
        id: 'income_aggregate',
        fromDatasetId: 'since_year',
        transform: [
          {
            type: 'ecSimpleTransform:aggregate',
            config: {
              resultDimensions: [
                { name: 'min', from: 'Income', method: 'min' },
                { name: 'Q1', from: 'Income', method: 'Q1' },
                { name: 'median', from: 'Income', method: 'median' },
                { name: 'Q3', from: 'Income', method: 'Q3' },
                { name: 'max', from: 'Income', method: 'max' },
                { name: 'Country', from: 'Country' }
              ],
              groupBy: 'Country'
            }
          },
          {
            type: 'sort',
            config: {
              dimension: 'Q3',
              order: 'asc'
            }
          }
        ]
      }
    ],
    title: {
      text: 'Income since 1950'
    },
    tooltip: {
      trigger: 'axis',
      confine: true
    },
    xAxis: {
      name: 'Income',
      nameLocation: 'middle',
      nameGap: 30,
      scale: true
    },
    yAxis: {
      type: 'category'
    },
    grid: {
      bottom: 140
    },
    legend: {
      selected: { detail: false }
    },
    dataZoom: [
      {
        type: 'inside'
      },
      {
        type: 'slider',
        height: 20,
        bottom: 60
      }
    ],
    series: [
      {
        name: 'boxplot',
        type: 'boxplot',
        datasetId: 'income_aggregate',
        itemStyle: {
          color: '#b8c5f2'
        },
        encode: {
          x: ['min', 'Q1', 'median', 'Q3', 'max'],
          y: 'Country',
          itemName: ['Country'],
          tooltip: ['min', 'Q1', 'median', 'Q3', 'max']
        }
      },
      {
        name: 'detail',
        type: 'scatter',
        datasetId: 'since_year',
        symbolSize: 6,
        tooltip: {
          trigger: 'item'
        },
        label: {
          show: true,
          position: 'top',
          align: 'left',
          verticalAlign: 'middle',
          rotate: 90,
          fontSize: 12
        },
        itemStyle: {
          color: '#d00000'
        },
        encode: {
          x: 'Income',
          y: 'Country',
          label: 'Year',
          itemName: 'Year',
          tooltip: ['Country', 'Year', 'Income']
        }
      }
    ]
  };
  myChart.setOption(option);
}
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
- This is an official ECharts example from `data-transform-aggregate/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
