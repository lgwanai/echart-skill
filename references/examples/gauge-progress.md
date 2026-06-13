# 进度仪表盘 / Progress Gauge

**Category:** `gauge`
**Example dir:** `gauge-progress`

## Template
- **gauge/basic.html** — Gauge
Data format: `{ value: number, name?: string, max?: number }`

## Option Code
```javascript
option = {
  series: [
    {
      type: 'gauge',
      progress: {
        show: true,
        width: 18
      },
      axisLine: {
        lineStyle: {
          width: 18
        }
      },
      axisTick: {
        show: false
      },
      splitLine: {
        length: 15,
        lineStyle: {
          width: 2,
          color: '#999'
        }
      },
      axisLabel: {
        distance: 25,
        color: '#999',
        fontSize: 20
      },
      anchor: {
        show: true,
        showAbove: true,
        size: 25,
        itemStyle: {
          borderWidth: 10
        }
      },
      title: {
        show: false
      },
      detail: {
        valueAnimation: true,
        fontSize: 80,
        offsetCenter: [0, '70%']
      },
      data: [
        {
          value: 70
        }
      ]
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py gauge/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
