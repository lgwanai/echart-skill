# 某站点用户访问来源

**Category:** `pie`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=pie-simple
**Template:** pie/basic.html
**Data Format:** `[{name: string, value: number}, ...]`
**Features:** emphasis/hover effects

## Official Option Code

```javascript
/*
title: Referer of a Website
category: pie
titleCN: 某站点用户访问来源
difficulty: 0
*/
option = {
  title: {
    text: 'Referer of a Website',
    subtext: 'Fake Data',
    left: 'center'
  },
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: 'Access From',
      type: 'pie',
      radius: '50%',
      data: [
        { value: 1048, name: 'Search Engine' },
        { value: 735, name: 'Direct' },
        { value: 580, name: 'Email' },
        { value: 484, name: 'Union Ads' },
        { value: 300, name: 'Video Ads' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py pie/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
