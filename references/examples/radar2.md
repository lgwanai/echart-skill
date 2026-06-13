# 浏览器占比变化

**Category:** `radar`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=radar2
**Template:** examples/radar2.html
**Data Format:** `{ indicators: [{name: string, max: number}, ...], series: [{name: string, value: number[]}, ...] }`
**Features:** visualMap component required, area fill enabled, emphasis/hover effects

## Official Option Code

```javascript
/*
title: Proportion of Browsers
category: radar
titleCN: 浏览器占比变化
difficulty: 3
*/
option = {
  title: {
    text: 'Proportion of Browsers',
    subtext: 'Fake Data',
    top: 10,
    left: 10
  },
  tooltip: {
    trigger: 'item'
  },
  legend: {
    type: 'scroll',
    bottom: 10,
    data: (function () {
      var list = [];
      for (var i = 1; i <= 28; i++) {
        list.push(i + 2000 + '');
      }
      return list;
    })()
  },
  visualMap: {
    top: 'middle',
    right: 10,
    inRange: {
      color: ['red', 'yellow']
    },
    calculable: true
  },
  radar: {
    indicator: [
      { text: 'IE8-', max: 400 },
      { text: 'IE9+', max: 400 },
      { text: 'Safari', max: 400 },
      { text: 'Firefox', max: 400 },
      { text: 'Chrome', max: 400 }
    ]
  },
  series: (function () {
    var series = [];
    for (var i = 1; i <= 28; i++) {
      series.push({
        type: 'radar',
        symbol: 'none',
        lineStyle: {
          width: 1
        },
        emphasis: {
          areaStyle: {
            color: 'rgba(0,250,0,0.3)'
          }
        },
        data: [
          {
            value: [
              (40 - i) * 10,
              (38 - i) * 4 + 60,
              i * 5 + 10,
              i * 9,
              (i * i) / 2
            ],
            name: i + 2000 + ''
          }
        ]
      });
    }
    return series;
  })()
};
```

## Usage
- Build: `scripts/build_template.py examples/radar2.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
