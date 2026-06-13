# 基础 K 线图 / Basic Candlestick

**Category:** `candlestick`
**Example dir:** `candlestick-simple`
**Difficulty:** 0

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
option = {
  xAxis: {
    data: ['2017-10-24', '2017-10-25', '2017-10-26', '2017-10-27']
  },
  yAxis: {},
  series: [
    {
      type: 'candlestick',
      data: [
        [20, 34, 10, 38],
        [40, 35, 30, 50],
        [31, 38, 33, 44],
        [38, 15, 5, 42]
      ]
    }
  ]
};
```



## Key Points
- This is an official ECharts example from `candlestick-simple/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
