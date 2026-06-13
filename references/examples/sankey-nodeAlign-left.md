# 桑基图左对齐布局 / Node Align Left in Sankey

**Category:** `sankey`
**Example dir:** `sankey-nodeAlign-left`
**Difficulty:** 3

## Template Match
- **sankey/basic.html** — Sankey

## Option Code
```javascript
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/data/energy.json', function (data) {
  myChart.hideLoading();
  myChart.setOption(
    (option = {
      title: {
        text: 'Node Align Left'
      },
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove'
      },
      series: [
        {
          type: 'sankey',
          emphasis: {
            focus: 'adjacency'
          },
          nodeAlign: 'left',
          data: data.nodes,
          links: data.links,
          lineStyle: {
            color: 'source',
            curveness: 0.5
          }
        }
      ]
    })
  );
});
```



## Key Points
- This is an official ECharts example from `sankey-nodeAlign-left/main.js`
- Template data format: `{ nodes: [{name: string, itemStyle?: {}}, ...], links: [{source: string, target: string, value: number}, ...] }`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
