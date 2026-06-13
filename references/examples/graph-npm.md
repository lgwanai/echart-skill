# NPM 依赖关系图

**Category:** `graph`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph-npm
**Template:** graph/force.html
**Data Format:** `{ nodes: [{id?, name, symbolSize?, category?, x?, y?}, ...], links: [{source, target, value?}, ...], categories?: [{name}, ...] }`
**Features:** per-item colors via itemStyle, emphasis/hover effects, labels displayed

## Official Option Code

```javascript
/*
title: NPM Dependencies
category: graph
titleCN: NPM 依赖关系图
difficulty: 9
*/
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

## Usage
- Build: `scripts/build_template.py graph/force.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
