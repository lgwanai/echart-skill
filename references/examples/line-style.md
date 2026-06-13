# 自定义折线图样式 / Line Style and Item Style

**Category:** `line`
**Example dir:** `line-style`

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
      data: [120, 200, 150, 80, 70, 110, 130],
      type: 'line',
      symbol: 'triangle',
      symbolSize: 20,
      lineStyle: {
        color: '#5470C6',
        width: 4,
        type: 'dashed'
      },
      itemStyle: {
        borderWidth: 3,
        borderColor: '#EE6666',
        color: 'yellow'
      }
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py line/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
