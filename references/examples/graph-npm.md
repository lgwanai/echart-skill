# graph-npm

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph-npm
**Chart Type:** `graph`

## User Data Requirements

Columns needed: need **nodes** [{name,...}] + **links/edges** [{source,target}]

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

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
