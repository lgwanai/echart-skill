# 基础折线图

**Category:** `line`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-simple
**Template:** line/basic.html
**Data Format:** `{ categories: string[], values: number[] }`

## Official Option Code

```javascript
/*
title: Basic Line Chart
category: line
titleCN: 基础折线图
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
      data: [150, 230, 224, 218, 135, 147, 260],
      type: 'line'
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py line/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
