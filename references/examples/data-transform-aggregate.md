# 简单的数据聚合 / Data Transform Simple Aggregate

**Category:** `boxplot`
**Example dir:** `data-transform-aggregate`

## Template
⚠️ No template — use knowledge base
Data format: `N/A`

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
        
```

## Key Points
- Generate via: `scripts/build_template.py  -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
