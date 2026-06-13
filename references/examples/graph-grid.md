# 笛卡尔坐标系上的 Graph / Graph on Cartesian

**Category:** `graph`
**Example dir:** `graph-grid`
**Difficulty:** 2

## Template Match
- **graph/force.html** — Force Graph

## Option Code
```javascript
const axisData = ['Mon', 'Tue', 'Wed', 'Very Loooong Thu', 'Fri', 'Sat', 'Sun'];
const data = axisData.map(function (item, i) {
  return Math.round(Math.random() * 1000 * (i + 1));
});
const links = data.map(function (item, i) {
  return {
    source: i,
    target: i + 1
  };
});
links.pop();
option = {
  title: {
    text: 'Graph on Cartesian'
  },
  tooltip: {},
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: axisData
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      type: 'graph',
      layout: 'none',
      coordinateSystem: 'cartesian2d',
      symbolSize: 40,
      label: {
        show: true
      },
      edgeSymbol: ['circle', 'arrow'],
      edgeSymbolSize: [4, 10],
      data: data,
      links: links,
      lineStyle: {
        color: '#2f4554'
      }
    }
  ]
};
```



## Key Points
- This is an official ECharts example from `graph-grid/main.js`
- Template data format: `{ nodes: [{id?, name, symbolSize?, category?, x?, y?}, ...], links: [{source, target, value?}, ...], categories?: [{name}, ...] }`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
