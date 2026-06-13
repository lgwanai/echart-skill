# 基础和弦图 / Basic Chord

**Category:** `chord`
**Example dir:** `chord-simple`

## Template
- **chord/basic.html** — Chord
Data format: `{ nodes: [{name: string}, ...], links: [{source: string, target: string, value: number}, ...] }`

## Option Code
```javascript
option = {
  tooltip: {},
  legend: {},
  series: [
    {
      type: 'chord',
      clockwise: false,
      label: { show: true },
      lineStyle: { color: 'target' },
      data: [{ name: 'A' }, { name: 'B' }, { name: 'C' }, { name: 'D' }],
      links: [
        { source: 'A', target: 'B', value: 40 },
        { source: 'A', target: 'C', value: 20 },
        { source: 'B', target: 'D', value: 20 }
      ]
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py chord/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
