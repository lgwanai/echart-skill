# 动态增加图节点

**Category:** `graph`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph-force-dynamic
**Template:** examples/graph-force-dynamic.html
**Data Format:** `{ nodes: [{id?, name, symbolSize?, category?, x?, y?}, ...], links: [{source, target, value?}, ...], categories?: [{name}, ...] }`

## Official Option Code

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

## Placeholders

| Placeholder | Type | Description |
|-------------|------|-------------|
| `{{{TITLE}}}` | string | title |

## Usage
- Build: `scripts/build_template.py examples/graph-force-dynamic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
