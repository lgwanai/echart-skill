# 饮品风味分类 / Drink Flavors

**Category:** `sunburst`
**Example dir:** `sunburst-drink`
**Difficulty:** 5

## Template Match
- **geo/lines.html** — 

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
          }
        ]
      },
      {
        name: 'Other Fruit',
        itemStyle: {
          color: '#dd4c51'
        },
        children: [
          {
            name: 'Coconut',
            value: 1,
            itemStyle: {
              color: '#f2684b'
            }
          },
          {
            name: 'Cherry',
            value: 1,
            itemStyle: {
              color: '#e73451'
            }
          },
          {
            name: 'Pomegranate',
            value: 1,
            itemStyle: {
              color: '#e65656'
            }
          },
          {
            name: 'Pineapple',
            value: 1,
            itemStyle: {
              color: '#f89a1c'
            }
          },
          {
            name: 'Grape',
            value: 1,
            itemStyle: {
              color: '#aeb92c'
            }
          },
          {
            name: 'Apple',
            value: 1,
            itemStyle: {
              color: '#4eb849'
       
```

## Relevant Debug Patterns
## #21
 — Sunburst 空白：RADIUS 字符串 + FOCUS 值非法
- **日期**：2026-06-13
- **现象**：20_Sunburst 一片空白
- **根因**：(1) `RADIUS: "['0%','90%']"` — 字符串假数组，同 #17 pie 的问题，`_json_safe` 将其当作字符串处理；(2) `FOCUS: "none"` — ECharts sunburst `emphasis.focus` 只接受 `'ancestor'` 或 `'descendant'`，不接受 `'none'`
- **修复**：(1) `RADIUS` 改为 `D(["0%","90%"])` — JSON 数组；(2) `FOCUS: "ancestor"`；(3) **模板增加防御**：`radius: {{RADIUS}} || ["0%","90%"]` 和 `focus: {{FOCUS}} || "ancestor"`

---
...

## Key Points
- This is an official ECharts example from `sunburst-drink/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
