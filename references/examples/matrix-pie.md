# matrix-pie

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=matrix-pie
**Chart Type:** `pie`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: need **name** + **value** columns
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

Data arrays to replace: **2**

## Reference Code

```javascript
/*
title: Pie Charts in Matrix
category: matrix
titleCN: 矩阵布局下的饼图
difficulty: 2
since: 6.0.0
*/
const xCnt = 9;
const yCnt = 6;
const series = [];
for (let i = 0; i < xCnt; ++i) {
  for (let j = 0; j < yCnt; ++j) {
    series.push({
      type: 'pie',
      coordinateSystem: 'matrix',
      center: [`Grade ${i + 1}`, `Class ${j + 1}`],
      radius: 18,
      data: [
        {
          value: Math.round(Math.random() * 10) + 10,
          name: 'Male'
        },
        {
          value: Math.round(Math.random() * 10) + 10,
          name: 'Female'
        }
      ],
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: false
        }
      }
    });
  }
}
option = {
  legend: {
    show: true,
    bottom: 40
  },
  matrix: {
    x: {
      data: [
        {
          value: 'Primary School',
          children: Array.from({ length: 5 }, (_, i) => {
            return `Grade ${i + 1}`;
          })
        },
        {
          value: 'High School',
          children: Array.from({ length: 4 }, (_, i) => {
            return `Grade ${i + 6}`;
          })
        }
      ]
    },
    y: {
      data: Array.from({ length: 6 }, (_, i) => {
        return `Class ${i + 1}`;
      })
    },
    top: 80,
    bottom: 80
  },
  series,
  tooltip: {
    show: true
  }
};
```
