# treemap-drill-down

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=treemap-drill-down
**Chart Type:** `treemap`

## User Data Requirements

Columns needed: need nested **name+value** or **name+children**

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `ec-option-doc-statistics-201604.json`:

```json
{
  "xAxis": {
    "axisLabel": {
      "$count": 2534,
      "show": {
        "$count": 444
      },
      "interval": {
        "$count": 950
      },
      "rotate": {
        "$count": 584
      },
      "inside": {
        "$count": 416
      },
      "formatter": {
        "$count": 886
      },
      "textStyle": {
        "$count": 490,
        "color": {
          "$count": 142
        },
        "fontStyle": {
          "$count": 107
        },
        "fontWeight": {
          "$coun
...
```

Agent: build DuckDB query to produce matching data structure.
## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: ECharts Option Query
category: treemap
titleCN: ECharts 配置项查询分布
*/
const uploadedDataURL =
  ROOT_PATH + '/data/asset/data/ec-option-doc-statistics-201604.json';
myChart.showLoading();
$.getJSON(uploadedDataURL, function (rawData) {
  myChart.hideLoading();
  function convert(source, target, basePath) {
    for (let key in source) {
      let path = basePath ? basePath + '.' + key : key;
      if (!key.match(/^\$/)) {
        target.children = target.children || [];
        const child = {
          name: path
        };
        target.children.push(child);
        convert(source[key], child, path);
      }
    }
    if (!target.children) {
      target.value = source.$count || 1;
    } else {
      target.children.push({
        name: basePath,
        value: source.$count
      });
    }
  }
  const data = {
    children: []
  };
  convert(rawData, data, '');
  myChart.setOption(
    (option = {
      title: {
        text: 'ECharts Options',
        subtext: '2016/04',
        left: 'leafDepth'
      },
      tooltip: {},
      series: [
        {
          name: 'option',
          type: 'treemap',
          visibleMin: 300,
          data: data.children,
          leafDepth: 2,
          levels: [
            {
              itemStyle: {
                borderColor: '#555',
                borderWidth: 4,
                gapWidth: 4
              }
            },
            {
              colorSaturation: [0.3, 0.6],
              itemStyle: {
                borderColorSaturation: 0.7,
                gapWidth: 2,
                borderWidth: 2
              }
            },
            {
              colorSaturation: [0.3, 0.5],
              itemStyle: {
                borderColorSaturation: 0.6,
                gapWidth: 1
              }
            },
            {
              colorSaturation: [0.3, 0.5]
            }
          ]
        }
      ]
    })
  );
});
```
