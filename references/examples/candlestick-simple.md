# 基础 K 线图

**Category:** `candlestick`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=candlestick-simple
**Template:** examples/candlestick-simple.html
**Data Format:** `{ dates: string[], values: [[open, close, low, high], ...] }`

## Official Option Code

```javascript
/*
title: Basic Candlestick
category: candlestick
titleCN: 基础 K 线图
difficulty: 0
*/
option = {
  xAxis: {
    data: ['2017-10-24', '2017-10-25', '2017-10-26', '2017-10-27']
  },
  yAxis: {},
  series: [
    {
      type: 'candlestick',
      data: [
        [20, 34, 10, 38],
        [40, 35, 30, 50],
        [31, 38, 33, 44],
        [38, 15, 5, 42]
      ]
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py examples/candlestick-simple.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
