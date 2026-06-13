# 基础平滑折线图

**Category:** `line`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-smooth
**Template:** line/basic.html
**Data Format:** `{ categories: string[], values: number[] }`

## Official Option Code

```javascript
/*
title: Smoothed Line Chart
category: line
titleCN: 基础平滑折线图
difficulty: 0
*/
option = {
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [820, 932, 901, 934, 1290, 1330, 1320],
      type: 'line',
      smooth: true
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py line/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
