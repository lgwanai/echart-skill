# 基础矩形树图 / Basic Treemap

**Category:** `treemap`
**Example dir:** `treemap-simple`

## Template
- **treemap/basic.html** — Treemap
Data format: `[{name: string, value?: number, children?: [...]}, ...]`

## Option Code
```javascript
option = {
  series: [
    {
      type: 'treemap',
      data: [
        {
          name: 'nodeA',
          value: 10,
          children: [
            {
              name: 'nodeAa',
              value: 4
            },
            {
              name: 'nodeAb',
              value: 6
            }
          ]
        },
        {
          name: 'nodeB',
          value: 20,
          children: [
            {
              name: 'nodeBa',
              value: 20,
              children: [
                {
                  name: 'nodeBa1',
                  value: 20
                }
              ]
            }
          ]
        }
      ]
    }
  ]
};
```

## Key Points
- Generate via: `scripts/build_template.py treemap/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
