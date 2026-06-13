# 关系图自动隐藏重叠标签

**Category:** `graph`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph-label-overlap
**Template:** graph/force.html
**Data Format:** `{ nodes: [{id?, name, symbolSize?, category?, x?, y?}, ...], links: [{source, target, value?}, ...], categories?: [{name}, ...] }`
**Features:** labels displayed

## Official Option Code

```javascript
/*
title: Hide Overlapped Label
category: graph
titleCN: 关系图自动隐藏重叠标签
difficulty: 3
*/
myChart.showLoading();
$.getJSON(ROOT_PATH + '/data/asset/data/les-miserables.json', function (graph) {
  myChart.hideLoading();
  option = {
    tooltip: {},
    legend: [
      {
        data: graph.categories.map(function (a) {
          return a.name;
        })
      }
    ],
    series: [
      {
        name: 'Les Miserables',
        type: 'graph',
        layout: 'none',
        data: graph.nodes,
        links: graph.links,
        categories: graph.categories,
        roam: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}'
        },
        labelLayout: {
          hideOverlap: true
        },
        scaleLimit: {
          min: 0.4,
          max: 2
        },
        lineStyle: {
          color: 'source',
          curveness: 0.3
        }
      }
    ]
  };
  myChart.setOption(option);
});
```

## Usage
- Build: `scripts/build_template.py graph/force.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
