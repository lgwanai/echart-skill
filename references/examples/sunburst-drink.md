# 饮品风味分类 / Drink Flavors

**Category:** `sunburst`
**Example dir:** `sunburst-drink`

## Template
- **sunburst/basic.html** — Sunburst
Data format: `[{name?: string, value?: number, itemStyle?: {}, children?: [...]}, ...]`

## Option Code
```javascript
var data = [
  {
    name: 'Flora',
    itemStyle: {
      color: '#da0d68'
    },
    children: [
      {
        name: 'Black Tea',
        value: 1,
        itemStyle: {
          color: '#975e6d'
        }
      },
      {
        name: 'Floral',
        itemStyle: {
          color: '#e0719c'
        },
        children: [
          {
            name: 'Chamomile',
            value: 1,
            itemStyle: {
              color: '#f99e1c'
            }
          },
          {
            name: 'Rose',
            value: 1,
            itemStyle: {
              color: '#ef5a78'
            }
          },
          {
            name: 'Jasmine',
            value: 1,
            itemStyle: {
              color: '#f7f1bd'
            }
          }
        ]
      }
    ]
  },
  {
    name: 'Fruity',
    itemStyle: {
      color: '#da1d23'
    },
    children: [
      {
        name: 'Berry',
        itemStyle: {
          color: '#dd4c51'
        },
        children: [
          {
            name: 'Blackberry',
            value: 1,
            itemStyle: {
              color: '#3e0317'
            }
          },
          {
            name: 'Raspberry',
            value: 1,
            itemStyle: {
              color: '#e62969'
            }
          },
          {
            name: 'Blueberry',
            value: 1,
            itemStyle: {
              color: '#6569b0'
            }
          },
          {
            name: 'Strawberry',
            value: 1,
            itemStyle: {
              color: '#ef2d36'
            }
          }
        ]
      },
      {
        name: 'Dried Fruit',
        itemStyle: {
          color: '#c94a44'
        },
        children: [
          {
            name: 'Raisin',
            value: 1,
            itemStyle: {
              color: '#b53b54'
            }
          },
          {
            name: 'Prune',
            value: 1,
            itemStyle: {
              color: '#a5446f'
            }
    
```

## Key Points
- Generate via: `scripts/build_template.py sunburst/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
