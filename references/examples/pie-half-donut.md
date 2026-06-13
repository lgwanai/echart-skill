# 半环形图

**Category:** `pie`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=pie-half-donut
**Template:** examples/pie-half-donut.html
**Data Format:** `[{name: string, value: number}, ...]`

## Official Option Code

```javascript
/*
title: Half Doughnut Chart
category: pie
titleCN: 半环形图
difficulty: 1
*/
// This example requires ECharts v5.5.0 or later
option = {
  tooltip: {
    trigger: 'item'
  },
  legend: {
    top: '5%',
    left: 'center'
  },
  series: [
    {
      name: 'Access From',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '70%'],
      // adjust the start and end angle
      startAngle: 180,
      endAngle: 360,
      data: [
        { value: 1048, name: 'Search Engine' },
        { value: 735, name: 'Direct' },
        { value: 580, name: 'Email' },
        { value: 484, name: 'Union Ads' },
        { value: 300, name: 'Video Ads' }
      ]
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py examples/pie-half-donut.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
