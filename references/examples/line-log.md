# 对数轴示例 / Log Axis

**Category:** `line`
**Example dir:** `line-log`

## Template
- **line/basic.html** — Line
Data format: `{ categories: string[], values: number[] }`

## Option Code
```javascript
option = {
  title: {
    text: 'Log Axis',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b} : {c}'
  },
  legend: {
    left: 'left'
  },
  xAxis: {
    type: 'category',
    name: 'x',
    splitLine: { show: false },
    data: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  yAxis: {
    type: 'log',
    name: 'y',
    minorSplitLine: {
      show: true
    }
  },
  series: [
    {
      name: 'Log2',
      type: 'line',
      data: [1, 3, 9, 27, 81, 247, 741, 2223, 6669]
    },
    {
      name: 'Log3',
      type: 'line',
      data: [1, 2, 4, 8, 16, 32, 64, 128, 256]
    },
    {
      name: 'Log1/2',
      type: 'line',
      data: [
        1 / 2,
        1 / 4,
        1 / 8,
        1 / 16,
        1 / 32,
        1 / 64,
        1 / 128,
        1 / 256,
        1 / 512
      ]
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py line/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
