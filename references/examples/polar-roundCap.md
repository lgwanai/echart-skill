# 圆角环形图

**Category:** `bar`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=polar-roundCap
**Template:** NONE — use knowledge base
**Data Format:** `N/A`

## Official Option Code

```javascript
/*
title: Rounded Bar on Polar
category: bar
titleCN: 圆角环形图
difficulty: 7
*/
option = {
  angleAxis: {
    max: 2,
    startAngle: 30,
    splitLine: {
      show: false
    }
  },
  radiusAxis: {
    type: 'category',
    data: ['v', 'w', 'x', 'y', 'z'],
    z: 10
  },
  polar: {},
  series: [
    {
      type: 'bar',
      data: [4, 3, 2, 1, 0],
      coordinateSystem: 'polar',
      name: 'Without Round Cap',
      itemStyle: {
        borderColor: 'red',
        opacity: 0.8,
        borderWidth: 1
      }
    },
    {
      type: 'bar',
      data: [4, 3, 2, 1, 0],
      coordinateSystem: 'polar',
      name: 'With Round Cap',
      roundCap: true,
      itemStyle: {
        borderColor: 'green',
        opacity: 0.8,
        borderWidth: 1
      }
    }
  ],
  legend: {
    show: true,
    data: ['Without Round Cap', 'With Round Cap']
  }
};
```

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
