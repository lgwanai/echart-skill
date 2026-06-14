# graph-force

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph-force

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Force Layout
category: graph
titleCN: 力引导布局
difficulty: 3
*/
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/data/les-miserables.json', function (graph) {
  myChart.hideLoading();
  graph.nodes.forEach(function (node) {
    node.symbolSize = 5;
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
    series: [
      {
        name: 'Les Miserables',
        type: 'graph',
        layout: 'force',
        data: graph.nodes,
        links: graph.links,
        categories: graph.categories,
        roam: true,
        label: {
          position: 'right'
        },
        force: {
          repulsion: 100
        }
      }
    ]
  };
  myChart.setOption(option);
});
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
