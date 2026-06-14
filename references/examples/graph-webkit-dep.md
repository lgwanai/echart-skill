# graph-webkit-dep

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph-webkit-dep
**Chart Type:** `graph`

## User Data Requirements

Columns needed: need **nodes** [{name,...}] + **links/edges** [{source,target}]

## Data Arrays — Complete Replacement Guide

**1 array(s)** to replace with real data:

### [0] `data` (context: legend)
```
data: ['HTMLElement', 'WebGL', 'SVG', 'CSS', 'Other']
```

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Graph Webkit Dep
category: graph
titleCN: WebKit 模块关系依赖图
shotWidth: 900
difficulty: 8
*/
myChart.showLoading();
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/data/webkit-dep.json', function (webkitDep) {
  myChart.hideLoading();
  option = {
    legend: {
      data: ['HTMLElement', 'WebGL', 'SVG', 'CSS', 'Other']
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        animation: false,
        roam: true,
        roamTrigger: 'global',
        scaleLimit: {
          max: 8,
          min: 0.5
        },
        label: {
          position: 'right',
          formatter: '{b}'
        },
        draggable: true,
        data: webkitDep.nodes.map(function (node, idx) {
          node.id = idx;
          return node;
        }),
        categories: webkitDep.categories,
        force: {
          edgeLength: 5,
          repulsion: 20,
          gravity: 0.2
        },
        edges: webkitDep.links
      }
    ],
    thumbnail: {
      width: '15%',
      height: '15%',
      windowStyle: {
        color: 'rgba(140, 212, 250, 0.5)',
        borderColor: 'rgba(30, 64, 175, 0.7)',
        opacity: 1
      }
    }
  };
  myChart.setOption(option);
});
```
