# 极坐标系下的堆叠柱状图

**Category:** `bar`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-polar-stack
**Template:** bar/basic.html
**Data Format:** `{ categories: string[], values: number[] }`
**Features:** emphasis/hover effects

## Official Option Code

```javascript
/*
title: Stacked Bar Chart on Polar
titleCN: 极坐标系下的堆叠柱状图
category: bar
difficulty: 7
*/
option = {
  angleAxis: {},
  radiusAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu'],
    z: 10
  },
  polar: {},
  series: [
    {
      type: 'bar',
      data: [1, 2, 3, 4],
      coordinateSystem: 'polar',
      name: 'A',
      stack: 'a',
      emphasis: {
        focus: 'series'
      }
    },
    {
      type: 'bar',
      data: [2, 4, 6, 8],
      coordinateSystem: 'polar',
      name: 'B',
      stack: 'a',
      emphasis: {
        focus: 'series'
      }
    },
    {
      type: 'bar',
      data: [1, 2, 3, 4],
      coordinateSystem: 'polar',
      name: 'C',
      stack: 'a',
      emphasis: {
        focus: 'series'
      }
    }
  ],
  legend: {
    show: true,
    data: ['A', 'B', 'C']
  }
};
```

## Usage
- Build: `scripts/build_template.py bar/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
