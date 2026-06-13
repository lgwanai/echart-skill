# 和弦图 minAngle / Chord minAngle

**Category:** `chord`
**Example dir:** `chord-minAngle`

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
      label: { show: true },
      minAngle: 30,
      data: [
        { name: 'A' },
        { name: 'B' },
        { name: 'C' },
        { name: 'D' },
        { name: 'E' },
        { name: 'F' }
      ],
      links: [
        { source: 'A', target: 'B', value: 40 },
        { source: 'B', target: 'C', value: 20 },
        { source: 'E', target: 'A', value: 5 }
      ]
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py chord/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
