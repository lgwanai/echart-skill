# 极坐标双数值轴

**Category:** `line`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-polar2
**Template:** line/basic.html
**Data Format:** `{ categories: string[], values: number[] }`

## Official Option Code

```javascript
/*
title: Two Value-Axes in Polar
category: line
titleCN: 极坐标双数值轴
difficulty: 10
*/
const data = [];
for (let i = 0; i <= 360; i++) {
  let t = (i / 180) * Math.PI;
  let r = Math.sin(2 * t) * Math.cos(2 * t);
  data.push([r, i]);
}
option = {
  title: {
    text: 'Two Value-Axes in Polar'
  },
  legend: {
    data: ['line']
  },
  polar: {
    center: ['50%', '54%']
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    }
  },
  angleAxis: {
    type: 'value',
    startAngle: 0
  },
  radiusAxis: {
    min: 0
  },
  series: [
    {
      coordinateSystem: 'polar',
      name: 'line',
      type: 'line',
      showSymbol: false,
      data: data
    }
  ],
  animationDuration: 2000
};
```

## Usage
- Build: `scripts/build_template.py line/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
