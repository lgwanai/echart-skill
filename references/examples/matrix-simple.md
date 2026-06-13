# 简单的矩阵图

**Category:** `matrix`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=matrix-simple
**Template:** NONE — use knowledge base
**Data Format:** `N/A`
**Features:** visualMap component required, labels displayed

## Official Option Code

```javascript
/*
title: Simple Matrix
category: matrix
titleCN: 简单的矩阵图
difficulty: 1
since: 6.0.0
*/
option = {
  matrix: {
    x: {
      data: [
        {
          value: 'A',
          children: [
            'A1',
            'A2',
            {
              value: 'A3',
              children: ['A31', 'A32']
            }
          ]
        }
      ]
    },
    y: {
      data: ['U', 'V']
    },
    top: 150,
    bottom: 150
  },
  visualMap: {
    type: 'continuous',
    min: 0,
    max: 80,
    top: 'middle',
    dimension: 2,
    calculable: true
  },
  series: {
    type: 'heatmap',
    coordinateSystem: 'matrix',
    data: [
      ['A1', 'U', 10],
      ['A1', 'V', 20],
      ['A2', 'U', 30],
      ['A2', 'V', 40],
      ['A31', 'U', 50],
      ['A3', 'V', 60]
    ],
    label: {
      show: true
    }
  }
};
```

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
