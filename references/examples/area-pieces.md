# 折线图区域高亮 / Area Pieces

**Category:** `'line, visualMap'`
**Example dir:** `area-pieces`

## Template
- **line/area-pieces.html** — Stacked Line / Area
Data format: `{ categories: string[], series: [{name: string, stack: string, data: number[]}, ...] }`

## Option Code


## Important
- Area chart = line chart with `AREA_STYLE: true`
- Use `line/basic.html` template

## Important
- Uses  — visualMap piecewise + markLine + smooth 0.6
- Data format: 
- Official example: area-pieces

## Key Points
- Generate via: `scripts/build_template.py line/stack.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
