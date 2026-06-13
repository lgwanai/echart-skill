# 基础南丁格尔玫瑰图 / Nightingale Chart

**Category:** `pie`
**Example dir:** `pie-roseType-simple`

## Template
- **pie/basic.html** — Pie
Data format: `[{name: string, value: number}, ...]`

## Option Code
```javascript
option = {
  legend: {
    top: 'bottom'
  },
  toolbox: {
    show: true,
    feature: {
      mark: { show: true },
      dataView: { show: true, readOnly: false },
      restore: { show: true },
      saveAsImage: { show: true }
    }
  },
  series: [
    {
      name: 'Nightingale Chart',
      type: 'pie',
      radius: [50, 250],
      center: ['50%', '50%'],
      roseType: 'area',
      itemStyle: {
        borderRadius: 8
      },
      data: [
        { value: 40, name: 'rose 1' },
        { value: 38, name: 'rose 2' },
        { value: 32, name: 'rose 3' },
        { value: 30, name: 'rose 4' },
        { value: 28, name: 'rose 5' },
        { value: 26, name: 'rose 6' },
        { value: 22, name: 'rose 7' },
        { value: 18, name: 'rose 8' }
      ]
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py pie/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
