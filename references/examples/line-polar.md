# 极坐标双数值轴 / Two Value-Axes in Polar

**Category:** `line`
**Example dir:** `line-polar`

## Template
- **line/basic.html** — Line
Data format: `{ categories: string[], values: number[] }`

## Option Code
```javascript
const data = [];
for (let i = 0; i <= 100; i++) {
  let theta = (i / 100) * 360;
  let r = 5 * (1 + Math.sin((theta / 180) * Math.PI));
  data.push([r, theta]);
}
option = {
  title: {
    text: 'Two Value-Axes in Polar'
  },
  legend: {
    data: ['line']
  },
  polar: {},
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
  radiusAxis: {},
  series: [
    {
      coordinateSystem: 'polar',
      name: 'line',
      type: 'line',
      data: data
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py line/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
