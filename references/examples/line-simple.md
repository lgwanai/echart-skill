# 基础折线图 / Basic Line Chart

**Category:** `line`
**Example dir:** `line-simple`

## Template
- **line/basic.html** — Line
Data format: `{ categories: string[], values: number[] }`

## Option Code
```javascript
option = {
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [150, 230, 224, 218, 135, 147, 260],
      type: 'line'
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py line/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
