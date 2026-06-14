# matrix-graph

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=matrix-graph

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

**3 data arrays** to replace:
- `data[0]`: `data: ['Data Analysis', 'Programming', 'Algorithms']`
- `data[1]`: `data: ['1st Year', '2nd Year', '3rd Year', '4th Year']`
- `data[2]`: `data: [
        ['Programming', '1st Year', 1, 'Intro to Computer Science']`

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Graph Chart in Matrix
category: matrix
titleCN: 矩阵布局下的关系图
difficulty: 2
since: 6.0.0
*/
const margin = [150, 80];
const width = myChart.getWidth() - margin[1] * 2;
const height = myChart.getHeight() - margin[0] * 2;
option = {
  title: {
    text: 'Course Prerequisites'
  },
  matrix: {
    x: {
      data: ['Data Analysis', 'Programming', 'Algorithms']
    },
    y: {
      data: ['1st Year', '2nd Year', '3rd Year', '4th Year']
    },
    left: margin[1],
    right: margin[1],
    top: margin[0],
    bottom: margin[0]
  },
  series: [
    {
      type: 'graph',
      coordinateSystem: 'matrix',
      edgeSymbol: ['none', 'arrow'],
      symbolSize: 15,
      links: [
        {
          source: 1,
          target: 0
        },
        {
          source: 2,
          target: 0
        },
        {
          source: 3,
          target: 0
        },
        {
          source: 4,
          target: 3
        },
        {
          source: 4,
          target: 2
        },
        {
          source: 5,
          target: 1
        },
        {
          source: 6,
          target: 3
        }
      ],
      data: [
        ['Programming', '1st Year', 1, 'Intro to Computer Science'],
        ['Data Analysis', '2nd Year', 1, 'Intro to Data Analysis'],
        ['Algorithms', '2nd Year', 1, 'Intro to Algorithms'],
        ['Programming', '2nd Year', 1, 'Advanced Programming'],
        ['Algorithms', '4th Year', 1, 'Data Structures\nand Algorithms'],
        ['Data Analysis', '3rd Year', 1, 'Statistics for Data Analysis'],
        ['Programming', '3rd Year', 1, 'Software Development']
      ],
      label: {
        show: true,
        formatter: (params) => {
          return params.data[3];
        },
        color: '#555',
        borderWidth: 0,
        fontSize: 15,
        fontWeight: 'bold',
        offset: [0, -15],
        verticalAlign: 'bottom'
      },
      lineStyle: {
        color: '#9af',
        width: 2,
        opacity: 1
      }
    }
  ],
  graphic: {
    elements: [
      {
        type: 'text',
        x: (width / 4) * 2.5 + margin[1],
        y: margin[0] - 15,
        style: {
          text: 'Course Categories',
          textAlign: 'center',
          textVerticalAlign: 'bottom',
          fontSize: 18,
          fontWeight: 'bold',
          fill: '#333'
        }
      },
      {
        type: 'text',
        x: margin[1] - 15,
        y: (height / 5) * 3 + margin[0],
        style: {
          text: 'Course Categories',
          textAlign: 'center',
          textVerticalAlign: 'bottom',
          fontSize: 18,
          fontWeight: 'bold',
          fill: '#333'
        },
        rotation: Math.PI / 2
      }
    ]
  }
};
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
