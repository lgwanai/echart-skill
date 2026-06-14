# GraphGL - GPU å¸å±

**Category:** `graphGL`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graphgl-gpu-layout
**Template:** examples/graphgl-gpu-layout.html
**Data Format:** `N/A`
**Features:** per-item colors via itemStyle

## Official Option Code

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

## Placeholders

| Placeholder | Type | Description |
|-------------|------|-------------|
| `{{{TITLE}}}` | string | title |

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
