# 力引导布局

**Category:** `graph`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph-force2
**Template:** graph/force.html
**Data Format:** `{ nodes: [{id?, name, symbolSize?, category?, x?, y?}, ...], links: [{source, target, value?}, ...], categories?: [{name}, ...] }`

## Official Option Code

```javascript
/*
title: Force Layout
category: graph
titleCN: 力引导布局
difficulty: 1
*/
function createNodes(count) {
  var nodes = [];
  for (var i = 0; i < count; i++) {
    nodes.push({
      id: i + ''
    });
  }
  return nodes;
}
function createEdges(count) {
  var edges = [];
  if (count === 2) {
    return [[0, 1]];
  }
  for (var i = 0; i < count; i++) {
    edges.push([i, (i + 1) % count]);
  }
  return edges;
}
var datas = [];
for (var i = 0; i < 16; i++) {
  datas.push({
    nodes: createNodes(i + 2),
    edges: createEdges(i + 2)
  });
}
option = {
  series: datas.map(function (item, idx) {
    return {
      type: 'graph',
      layout: 'force',
      animation: false,
      data: item.nodes,
      left: (idx % 4) * 25 + '%',
      top: Math.floor(idx / 4) * 25 + '%',
      width: '25%',
      height: '25%',
      force: {
        // initLayout: 'circular'
        // gravity: 0
        repulsion: 60,
        edgeLength: 2
      },
      edges: item.edges.map(function (e) {
        return {
          source: e[0] + '',
          target: e[1] + ''
        };
      })
    };
  })
};
```

## Usage
- Build: `scripts/build_template.py graph/force.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
