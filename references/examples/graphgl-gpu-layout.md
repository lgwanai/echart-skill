# graphgl-gpu-layout

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graphgl-gpu-layout

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: GraphGL - GPU Layout
category: graphGL
theme: dark
titleCN: GraphGL - GPU å¸å±
videoStart: 0
videoEnd: 10000
shotWidth: 1280
*/
function createNodes(widthCount, heightCount) {
  var nodes = [];
  for (var i = 0; i < widthCount; i++) {
    for (var j = 0; j < heightCount; j++) {
      nodes.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        value: 1
      });
    }
  }
  return nodes;
}
function createEdges(widthCount, heightCount) {
  var edges = [];
  for (var i = 0; i < widthCount; i++) {
    for (var j = 0; j < heightCount; j++) {
      if (i < widthCount - 1) {
        edges.push({
          source: i + j * widthCount,
          target: i + 1 + j * widthCount,
          value: 1
        });
      }
      if (j < heightCount - 1) {
        edges.push({
          source: i + j * widthCount,
          target: i + (j + 1) * widthCount,
          value: 1
        });
      }
    }
  }
  return edges;
}
var nodes = createNodes(50, 50);
var edges = createEdges(50, 50);
option = {
  series: [
    {
      type: 'graphGL',
      nodes: nodes,
      edges: edges,
      itemStyle: {
        color: 'rgba(255,255,255,0.8)'
      },
      lineStyle: {
        color: 'rgba(255,255,255,0.8)',
        width: 3
      },
      forceAtlas2: {
        steps: 5,
        jitterTolerence: 10,
        edgeWeightInfluence: 4
      }
    }
  ]
};
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
