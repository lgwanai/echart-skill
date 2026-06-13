# NPM 依赖关系图 / NPM Dependencies

**Category:** `graph`
**Example dir:** `graph-npm`

## Template
- **graph/force.html** — Force Graph
Data format: `{ nodes: [{id?, name, symbolSize?, category?, x?, y?}, ...], links: [{source, target, value?}, ...], categories?: [{name}, ...] }`

## Option Code
```javascript
myChart.showLoading();
$.getJSON(
  ROOT_PATH + '/data/asset/data/npmdepgraph.min10.json',
  function (json) {
    myChart.hideLoading();
    myChart.setOption(
      (option = {
        title: {
          text: 'NPM Dependencies'
        },
        animationDurationUpdate: 1500,
        animationEasingUpdate: 'quinticInOut',
        series: [
          {
            type: 'graph',
            layout: 'none',
            // progressiveThreshold: 700,
            data: json.nodes.map(function (node) {
              return {
                x: node.x,
                y: node.y,
                id: node.id,
                name: node.label,
                symbolSize: node.size,
                itemStyle: {
                  color: node.color
                }
              };
            }),
            edges: json.edges.map(function (edge) {
              return {
                source: edge.sourceID,
                target: edge.targetID
              };
            }),
            emphasis: {
              focus: 'adjacency',
              label: {
                position: 'right',
                show: true
              }
            },
            roam: true,
            roamTrigger: 'global',
            lineStyle: {
              width: 0.5,
              curveness: 0.3,
              opacity: 0.7
            }
          }
        ],
        thumbnail: {
          width: '20%',
          height: '20%',
          windowStyle: {
            color: 'rgba(140, 212, 250, 0.5)',
            borderColor: 'rgba(30, 64, 175, 0.7)',
            opacity: 1
          }
        }
      }),
      true
    );
  }
);
```

## Key Points
- Generate via: `scripts/build_template.py graph/force.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
