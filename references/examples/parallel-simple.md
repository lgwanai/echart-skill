# 基础平行坐标 / Basic Parallel

**Category:** `parallel`
**Example dir:** `parallel-simple`
**Difficulty:** 1

## Template Match
- **parallel/basic.html** — Parallel Coordinates

## Option Code
```javascript
option = {
  parallelAxis: [
    { dim: 0, name: 'Price' },
    { dim: 1, name: 'Net Weight' },
    { dim: 2, name: 'Amount' },
    {
      dim: 3,
      name: 'Score',
      type: 'category',
      data: ['Excellent', 'Good', 'OK', 'Bad']
    }
  ],
  series: {
    type: 'parallel',
    lineStyle: {
      width: 4
    },
    data: [
      [12.99, 100, 82, 'Good'],
      [9.99, 80, 77, 'OK'],
      [20, 120, 60, 'Excellent']
    ]
  }
};
```



## Key Points
- This is an official ECharts example from `parallel-simple/main.js`
- Template data format: `[[dim1, dim2, dim3, ...], ...]  (parallelAxis defines each dimension)`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
