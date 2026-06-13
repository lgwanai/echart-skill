# 最简单的数据集（dataset）

**Category:** `'dataset, bar'`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=dataset-simple0
**Template:** examples/dataset-simple0.html
**Data Format:** `N/A`
**Features:** uses dataset (not series.data)

## Official Option Code

```javascript
/*
title: Simple Example of Dataset
category: 'dataset, bar'
titleCN: 最简单的数据集（dataset）
difficulty: 5
*/
option = {
  legend: {},
  tooltip: {},
  dataset: {
    source: [
      ['product', '2015', '2016', '2017'],
      ['Matcha Latte', 43.3, 85.8, 93.7],
      ['Milk Tea', 83.1, 73.4, 55.1],
      ['Cheese Cocoa', 86.4, 65.2, 82.5],
      ['Walnut Brownie', 72.4, 53.9, 39.1]
    ]
  },
  xAxis: { type: 'category' },
  yAxis: {},
  // Declare several bar series, each will be mapped
  // to a column of dataset.source by default.
  series: [{ type: 'bar' }, { type: 'bar' }, { type: 'bar' }]
};
```

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
