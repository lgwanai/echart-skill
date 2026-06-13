# 动态增加图节点 / Graph Dynamic

**Category:** `graph`
**Example dir:** `graph-force-dynamic`

## Template
- **graph/force.html** — Force Graph
Data format: `{ nodes: [{id?, name, symbolSize?, category?, x?, y?}, ...], links: [{source, target, value?}, ...], categories?: [{name}, ...] }`

## Option Code
```javascript
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

## Key Points
- Generate via: `scripts/build_template.py graph/force.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
