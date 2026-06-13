# 矩阵中响应式网格布局 / Responsive grid layout based on matrix

**Category:** `matrix`
**Example dir:** `matrix-grid-layout`
**Difficulty:** 3

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
let _idBase = 1;
const _mediaDefinitionList = [
  {
    // When the canvas width is less than 500px,
    query: { maxWidth: 500 },
    matrix: {
      // Define column and rows
      x: { data: Array(1).fill(null) },
      y: { data: Array(10).fill(null) }
    },
    // Place sections into the matrix cell determined by the coords.
    // key: sectionId, value: coord.
    sectionCoordMap: {
      section_title_1: [0, 0],
      section_header_1: [0, [1, 2]],
      section_sidebar_1: [0, [3, 4]],
      section_main_content_area_1: [0, [5, 7]],
      section_footer_1: [0, [8, 9]]
    }
  },
  {
    // The default (with no `query`)
    matrix: {
      // Define column and rows
      x: { data: Array(4).fill(null) },
      y: { data: Array(10).fill(null) }
    },
    sectionCoordMap: {
      section_title_1: [[0, 3], 0],
      section_header_1: [
        [0, 3],
        [1, 2]
      ],
      section_sidebar_1: [0, [3, 9]],
      section_main_content_area_1: [
        [1, 3],
        [3, 7]
      ],
      section_footer_1: [
        [1, 3],
        [8, 9]
      ]
    }
  }
];

const _sectionDefinitionMap = {
  section_title_1: {
    option: {
      title: [
        {
          coordinateSystem: 'matrix',
          text: 'Resize the Canvas to Check the Responsiveness',
          left: 'center',
          top: 10
        }
      ]
    }
  },
  section_header_1: {
    option: {
      title: [
        {
          coordinateSystem: 'matrix',
          text: 'Header Section',
          textStyle: { fontSize: 14 },
          left: 'center',
          top: 5
        }
      ],
      xAxis: {
        type: 'time',
        id: 'header_1',
        gridId: 'header_1'
      },
      yAxis: {
        id: 'header_1',
        gridId: 'header_1',
        splitNumber: 2,
        splitLine: { show: false }
      },
      grid: {
        id: 'header_1',
        coordinateSystem: 'matrix',
        tooltip: {
          trigger: 'axis'
        },
        top: 30,
        bottom: 10,
        left: 10,
        right: 10,
        outerBounds: {
          top: 30,
          left: 20,
          bottom: 20,
          right: 20
        }
      },
      series: {
        type: 'line',
        id: 'header_1',
        xAxisId: 'header_1',
        yAxisId: 'header_1',
        symbol: 'none',
        data: generateSingleSeriesData(100, false)
      }
    }
  },
  section_sidebar_1: {
    option: {
      title: {
        coordinateSystem: 'matrix',
        text: 'Sidebar Section',
        textStyle: { fontSize: 14 },
        left: 'center',
        top: 15
      },
      xAxis: {
        id: 'sidebar_1',
        gridId: 'sidebar_1',
        splitLine: { show: false },
        axisLabel: {
          hideOverlap: true
        }
      },
      yAxis: {
        type: 'time',
        id: 'sidebar_1',
        gridId: 'sidebar_1',
        axisLabel: {
          hideOverlap: true
        }
      },
      grid: {
        id: 'sidebar_1',
        coordinateSystem: 'matrix',
        tooltip: {
     
```



## Key Points
- This is an official ECharts example from `matrix-grid-layout/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
