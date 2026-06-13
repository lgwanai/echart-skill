# 自定义单个柱子颜色 / Set Style of Single Bar.

**Category:** `bar`
**Example dir:** `bar-data-color`

## Template
- **bar/basic.html** — Bar
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
      data: [
        120,
        {
          value: 200,
          itemStyle: {
            color: '#505372'
          }
        },
        150,
        80,
        70,
        110,
        130
      ],
      type: 'bar'
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py bar/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
