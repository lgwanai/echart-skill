# 笛卡尔坐标系上的 Graph

**Category:** `graph`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph-grid
**Template:** examples/graph-grid.html
**Data Format:** `{ nodes: [{name, x, y, symbolSize?}, ...], links: [{source, target}, ...] }`
**Features:** labels displayed

## Official Option Code

```javascript
/*
title: Graph on Cartesian
category: graph
titleCN: 笛卡尔坐标系上的 Graph
difficulty: 2
*/
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

## Usage
- Build: `scripts/build_template.py graph/static.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
