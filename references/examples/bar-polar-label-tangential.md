# 极坐标柱状图标签

**Category:** `bar`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-polar-label-tangential
**Template:** examples/bar-polar-label-tangential.html
**Data Format:** `{ categories: string[], values: number[] }`
**Features:** labels displayed

## Official Option Code

```javascript
/*
title: Tangential Polar Bar Label Position
titleCN: 极坐标柱状图标签
category: bar
difficulty: 2
*/
option = {
  title: [
    {
      text: 'Tangential Polar Bar Label Position (middle)'
    }
  ],
  polar: {
    radius: [30, '80%']
  },
  angleAxis: {
    max: 4,
    startAngle: 75
  },
  radiusAxis: {
    type: 'category',
    data: ['a', 'b', 'c', 'd']
  },
  tooltip: {},
  series: {
    type: 'bar',
    data: [2, 1.2, 2.4, 3.6],
    coordinateSystem: 'polar',
    label: {
      show: true,
      position: 'middle',
      formatter: '{b}: {c}'
    }
  }
};
```

## Usage
- Build: `scripts/build_template.py examples/bar-polar-label-tangential.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
