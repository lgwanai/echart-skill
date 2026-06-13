# 基础平行坐标

**Category:** `parallel`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=parallel-simple
**Template:** parallel/basic.html
**Data Format:** `[[dim1, dim2, dim3, ...], ...]  (parallelAxis defines each dimension)`

## Official Option Code

```javascript
/*
title: Basic Parallel
category: parallel
titleCN: 基础平行坐标
difficulty: 1
*/
option = {
  parallelAxis: [
    { dim: 0, name: 'Price' },
    { dim: 1, name: 'Net Weight' },
    { dim: 2, name: 'Amount' },
    {
      dim: 3,
      name: 'Score',
      type: 'category',
      data: ['Excellent', 'Good', 'OK', 'Bad']
    }
  ],
  series: {
    type: 'parallel',
    lineStyle: {
      width: 4
    },
    data: [
      [12.99, 100, 82, 'Good'],
      [9.99, 80, 77, 'OK'],
      [20, 120, 60, 'Excellent']
    ]
  }
};
```

## Usage
- Build: `scripts/build_template.py parallel/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
