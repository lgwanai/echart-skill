# graph-force2

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph-force2
**Chart Type:** `graph`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

## Reference Code

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
