# 环形图 / Doughnut Chart

**Category:** `pie`
**Example dir:** `pie-doughnut`

## Template
- **pie/basic.html** — Pie
Data format: `[{name: string, value: number}, ...]`

## Option Code
```javascript
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
      avoidLabelOverlap: false,
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 40,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
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
