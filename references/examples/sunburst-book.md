# 书籍分布 / Book Records

**Category:** `sunburst`
**Example dir:** `sunburst-book`
**Difficulty:** 6

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
const colors = ['#FFAE57', '#FF7853', '#EA5151', '#CC3F57', '#9A2555'];
const bgColor = '#2E2733';
const itemStyle = {
  star5: {
    color: colors[0]
  },
  star4: {
    color: colors[1]
  },
  star3: {
    color: colors[2]
  },
  star2: {
    color: colors[3]
  }
};
const data = [
  {
    name: '虚构',
    itemStyle: {
      color: colors[1]
    },
    children: [
      {
        name: '小说',
        children: [
          {
            name: '5☆',
            children: [
              {
                name: '疼'
              },
              {
                name: '慈悲'
              },
              {
                name: '楼下的房客'
              }
            ]
          },
          {
            name: '4☆',
            children: [
              {
                name: '虚无的十字架'
              },
              {
                name: '无声告白'
              },
              {
                name: '童年的终结'
              }
            ]
          },
          {
            name: '3☆',
            children: [
              {
                name: '疯癫老人日记'
              }
            ]
          }
        ]
      },
      {
        name: '其他',
        children: [
          {
            name: '5☆',
            children: [
              {
                name: '纳博科夫短篇小说全集'
              }
            ]
          },
          {
            name: '4☆',
            children: [
              {
                name: '安魂曲'
              },
              {
                name: '人生拼图版'
              }
            ]
          },
          {
            name: '3☆',
            children: [
              {
                name: '比起爱你，我更需要你'
              }
            ]
          }
        ]
      }
    ]
  },
  {
    name: '非虚构',
    itemStyle: {
      color: colors[2]
    },
    children: [
      {
        name: '设计',
        children: [
          {
            name: '5☆',
            children: [
              {
                name: '无界面交互'
              }
            ]
          },
          {
            name: '4☆',
            children: [
              {
                name: '数字绘图的光照与渲染技术'
              },
              {
                name: '日本建筑解剖书'
              }
            ]
          },
          {
            name: '3☆',
            children: [
              {
                name: '奇幻世界艺术\n&RPG地图绘制讲座'
              }
            ]
          }
        ]
      },
      {
        name: '社科',
        children: [
          {
            name: '5☆',
            children: [
              {
                name: '痛点'
              }
            ]
          },
          {
            name: '4☆',
            children: [
              {
                name: '卓有成效的管理者'
              },
              {
                name: '进化'
              },
              {
                name: '后物欲时代的来临'
              }
            ]
          },
          {
            name: '3☆',
            children: [
              {
                name: '疯癫与文明'
              }
    
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
- This is an official ECharts example from `sunburst-book/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
