# 矩阵中响应式网格布局 / Responsive grid layout based on matrix

**Category:** `matrix`
**Example dir:** `matrix-grid-layout`

## Template
⚠️ No template — use knowledge base
Data format: `N/A`

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
        left
```

## Key Points
- Generate via: `scripts/build_template.py  -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
