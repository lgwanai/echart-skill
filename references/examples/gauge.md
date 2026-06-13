# 基础仪表盘 / Gauge Basic chart

**Category:** `gauge`
**Example dir:** `gauge`
**Difficulty:** 1

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
option = {
  tooltip: {
    formatter: '{a} <br/>{b} : {c}%'
  },
  series: [
    {
      name: 'Pressure',
      type: 'gauge',
      detail: {
        formatter: '{value}'
      },
      data: [
        {
          value: 50,
          name: 'SCORE'
        }
      ]
    }
  ]
};
```



## Key Points
- This is an official ECharts example from `gauge/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
