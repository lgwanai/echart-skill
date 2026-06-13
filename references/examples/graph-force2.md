# 力引导布局 / Force Layout

**Category:** `graph`
**Example dir:** `graph-force2`
**Difficulty:** 1

## Template Match
- **graph/force.html** — Force Graph

## Option Code
```javascript
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



## Key Points
- This is an official ECharts example from `graph-force2/main.js`
- Template data format: `{ nodes: [{id?, name, symbolSize?, category?, x?, y?}, ...], links: [{source, target, value?}, ...], categories?: [{name}, ...] }`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
