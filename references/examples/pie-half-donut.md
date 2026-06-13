# 半环形图 / Half Doughnut Chart

**Category:** `pie`
**Example dir:** `pie-half-donut`

## Template
- **pie/basic.html** — Pie
Data format: `[{name: string, value: number}, ...]`

## Option Code
```javascript
// This example requires ECharts v5.5.0 or later
option = {
  tooltip: {
    trigger: 'item'
  },
  legend: {
    top: '5%',
    left: 'center'
  },
  series: [
    {
      name: 'Access From',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '70%'],
      // adjust the start and end angle
      startAngle: 180,
      endAngle: 360,
      data: [
        { value: 1048, name: 'Search Engine' },
        { value: 735, name: 'Direct' },
        { value: 580, name: 'Email' },
        { value: 484, name: 'Union Ads' },
        { value: 300, name: 'Video Ads' }
      ]
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py pie/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
