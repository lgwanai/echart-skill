# 基础面积图 / Basic area chart

**Category:** `line`
**Example dir:** `area-basic`

## Template
- **line/stack.html** — Stacked Line / Area
Data format: `{ categories: string[], series: [{name: string, stack: string, data: number[]}, ...] }`

## Option Code
```javascript
option = {
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [820, 932, 901, 934, 1290, 1330, 1320],
      type: 'line',
      areaStyle: {}
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py line/stack.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
