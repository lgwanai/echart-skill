# 极坐标柱状图标签 / Radial Polar Bar Label Position

**Category:** `bar`
**Example dir:** `bar-polar-label-radial`

## Template
- **bar/basic.html** — Bar
Data format: `{ categories: string[], values: number[] }`

## Option Code
```javascript
option = {
  title: [
    {
      text: 'Radial Polar Bar Label Position (middle)'
    }
  ],
  polar: {
    radius: [30, '80%']
  },
  radiusAxis: {
    max: 4
  },
  angleAxis: {
    type: 'category',
    data: ['a', 'b', 'c', 'd'],
    startAngle: 75
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
  },
  animation: false
};
```

## Key Points
- Generate via: `scripts/build_template.py bar/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
