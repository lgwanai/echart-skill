# graph-force-dynamic

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph-force-dynamic
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
title: Graph Dynamic
category: graph
shotDelay: 5000
titleCN: 动态增加图节点
difficulty: 6
*/
const data = [
  {
    fixed: true,
    x: myChart.getWidth() / 2,
    y: myChart.getHeight() / 2,
    symbolSize: 20,
    id: '-1'
  }
];
const edges = [];
option = {
  series: [
    {
      type: 'graph',
      layout: 'force',
      animation: false,
      data: data,
      force: {
        // initLayout: 'circular'
        // gravity: 0
        repulsion: 100,
        edgeLength: 5
      },
      edges: edges
    }
  ]
};
setInterval(function () {
  data.push({
    id: data.length + ''
  });
  var source = Math.round((data.length - 1) * Math.random());
  var target = Math.round((data.length - 1) * Math.random());
  if (source !== target) {
    edges.push({
      source: source,
      target: target
    });
  }
  myChart.setOption({
    series: [
      {
        roam: true,
        data: data,
        edges: edges
      }
    ]
  });
  // console.log('nodes: ' + data.length);
  // console.log('links: ' + data.length);
}, 200);
```
