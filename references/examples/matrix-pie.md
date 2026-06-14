# 矩阵布局下的饼图

**Category:** `matrix`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=matrix-pie
**Template:** examples/matrix-pie.html
**Data Format:** `N/A`
**Features:** emphasis/hover effects, labels displayed

## Official Option Code

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

## Placeholders

| Placeholder | Type | Description |
|-------------|------|-------------|
| `{{{TITLE}}}` | string | title |

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
