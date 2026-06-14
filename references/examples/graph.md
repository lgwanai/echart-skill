# graph

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph
**Chart Type:** `graph`

## User Data Requirements

Columns needed: need **nodes** [{name,...}] + **links/edges** [{source,target}]

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `les-miserables.json`:

```json
[
  {
    "id": "0",
    "name": "Myriel",
    "symbolSize": 19.12381,
    "x": -266.82776,
    "y": 299.6904,
    "value": 28.685715,
    "category": 0
  },
  {
    "id": "1",
    "name": "Napoleon",
    "symbolSize": 2.6666666666666665,
    "x": -418.08344,
    "y": 446.8853,
    "value": 4,
    "category": 0
  },
  {
    "id": "2",
    "name": "MlleBaptistine",
    "symbolSize": 6.323809333333333,
    "x": -212.76357,
    "y": 245.29176,
    "value": 9.485714,
    "category": 1
  }
]
```

Agent: build DuckDB query to produce matching data structure.
## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Les Miserables
category: graph
titleCN: 悲惨世界人物关系图
difficulty: 4
*/
myChart.showLoading();
$.getJSON(ROOT_PATH + '/data/asset/data/les-miserables.json', function (graph) {
  myChart.hideLoading();
  graph.nodes.forEach(function (node) {
    node.label = {
      show: node.symbolSize > 30
    };
  });
  option = {
    title: {
      text: 'Les Miserables',
      subtext: 'Default layout',
      top: 'bottom',
      left: 'right'
    },
    tooltip: {},
    legend: [
      {
        // selectedMode: 'single',
        data: graph.categories.map(function (a) {
          return a.name;
        })
      }
    ],
    animationDuration: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
      {
        name: 'Les Miserables',
        type: 'graph',
        legendHoverLink: false,
        layout: 'none',
        data: graph.nodes,
        links: graph.links,
        categories: graph.categories,
        roam: true,
        label: {
          position: 'right',
          formatter: '{b}'
        },
        lineStyle: {
          color: 'source',
          curveness: 0.3
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 10
          }
        }
      }
    ]
  };
  myChart.setOption(option);
});
```
