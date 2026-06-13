# WebKit 模块关系依赖图 / Graph Webkit Dep

**Category:** `graph`
**Example dir:** `graph-webkit-dep`
**Difficulty:** 8

## Template Match
- **graph/force.html** — Force Graph

## Option Code
```javascript
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



## Key Points
- This is an official ECharts example from `graph-webkit-dep/main.js`
- Template data format: `{ nodes: [{id?, name, symbolSize?, category?, x?, y?}, ...], links: [{source, target, value?}, ...], categories?: [{name}, ...] }`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
