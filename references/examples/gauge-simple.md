# 带标签数字动画的基础仪表盘 / Simple Gauge

**Category:** `gauge`
**Example dir:** `gauge-simple`

## Template
- **gauge/basic.html** — Gauge
Data format: `{ value: number, name?: string, max?: number }`

## Option Code
```javascript
option = {
  tooltip: {
    formatter: '{a} <br/>{b} : {c}%'
  },
  series: [
    {
      name: 'Pressure',
      type: 'gauge',
      progress: {
        show: true
      },
      detail: {
        valueAnimation: true,
        formatter: '{value}'
      },
      data: [
        {
          value: 50,
          name: 'SCORE'
        }
      ]
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py gauge/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
