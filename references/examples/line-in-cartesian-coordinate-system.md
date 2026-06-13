# 双数值轴折线图 / Line Chart in Cartesian Coordinate System

**Category:** `line`
**Example dir:** `line-in-cartesian-coordinate-system`

## Template
- **line/xy.html** — Cartesian Line
Data format: `[[x, y], [x, y], ...]`

## Option Code
```javascript
option = {
  xAxis: {},
  yAxis: {},
  series: [
    {
      data: [
        [10, 40],
        [50, 100],
        [40, 20]
      ],
      type: 'line'
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py line/xy.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
