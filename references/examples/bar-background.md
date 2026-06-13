# 带背景色的柱状图

**Category:** `bar`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-background
**Template:** examples/bar-background.html
**Data Format:** `{ categories: string[], values: number[] }`

## Official Option Code

```javascript
/*
title: Bar with Background
category: bar
titleCN: 带背景色的柱状图
difficulty: 1
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
      data: [120, 200, 150, 80, 70, 110, 130],
      type: 'bar',
      showBackground: true,
      backgroundStyle: {
        color: 'rgba(180, 180, 180, 0.2)'
      }
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py examples/bar-background.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
