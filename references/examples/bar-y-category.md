# 世界人口总量 - 条形图 / World Population

**Category:** `bar`
**Example dir:** `bar-y-category`

## Template
- **bar/horizontal.html** — Horizontal Bar
Data format: `{ categories: string[], values: number[] }`

## Option Code
```javascript
option = {
  title: {
    text: 'World Population'
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {},
  xAxis: {
    type: 'value',
    boundaryGap: [0, 0.01]
  },
  yAxis: {
    type: 'category',
    data: ['Brazil', 'Indonesia', 'USA', 'India', 'China', 'World']
  },
  series: [
    {
      name: '2011',
      type: 'bar',
      data: [18203, 23489, 29034, 104970, 131744, 630230]
    },
    {
      name: '2012',
      type: 'bar',
      data: [19325, 23438, 31000, 121594, 134141, 681807]
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py bar/horizontal.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
