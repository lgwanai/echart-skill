# 单色旭日图 / Monochrome Sunburst

**Category:** `sunburst`
**Example dir:** `sunburst-monochrome`
**Difficulty:** 3

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
const item1 = {
  color: '#F54F4A'
};
const item2 = {
  color: '#FF8C75'
};
const item3 = {
  color: '#FFB499'
};
const data = [
  {
    children: [
      {
        value: 5,
        children: [
          {
            value: 1,
            itemStyle: item1
          },
          {
            value: 2,
            children: [
              {
                value: 1,
                itemStyle: item2
              }
            ]
          },
          {
            children: [
              {
                value: 1
              }
            ]
          }
        ],
        itemStyle: item1
      },
      {
        value: 10,
        children: [
          {
            value: 6,
            children: [
              {
                value: 1,
                itemStyle: item1
              },
              {
                value: 1
              },
              {
                value: 1,
                itemStyle: item2
              },
              {
                value: 1
              }
            ],
            itemStyle: item3
          },
          {
            value: 2,
            children: [
              {
                value: 1
              }
            ],
            itemStyle: item3
          },
          {
            children: [
              {
                value: 1,
                itemStyle: item2
              }
            ]
          }
        ],
        itemStyle: item1
      }
    ],
    itemStyle: item1
  },
  {
    value: 9,
    children: [
      {
        value: 4,
        children: [
          {
            value: 2,
            itemStyle: item2
          },
          {
            children: [
              {
                value: 1,
                itemStyle: item1
              }
            ]
          }
        ],
        itemStyle: item1
      },
      {
        children: [
          {
            value: 3,
            children: [
              {
                value: 1
              },
              {
                value: 1,
                itemStyle: item2
              }
            ]
          }
        ],
        itemStyle: item3
      }
    ],
    itemStyle: item2
  },
  {
    value: 7,
    children: [
      {
        children: [
          {
            value: 1,
            itemStyle: item3
          },
          {
            value: 3,
            children: [
              {
                value: 1,
                itemStyle: item2
              },
              {
                value: 1
              }
            ],
            itemStyle: item2
          },
          {
            value: 2,
            children: [
              {
                value: 1
              },
              {
                value: 1,
                itemStyle: item1
              }
            ],
            itemStyle: item1
          }
        ],
        itemStyle: item3
      }
    ],
    itemStyle: item1
  },
  {
    children: [
      {
        value: 6,
        children: [
          {
            va
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
- This is an official ECharts example from `sunburst-monochrome/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
