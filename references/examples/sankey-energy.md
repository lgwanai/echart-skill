# 桑基图渐变色边 / Gradient Edge

**Category:** `sankey`
**Example dir:** `sankey-energy`
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
        text: 'Sankey Diagram'
      },
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove'
      },
      series: [
        {
          type: 'sankey',
          data: data.nodes,
          links: data.links,
          emphasis: {
            focus: 'adjacency'
          },
          lineStyle: {
            color: 'gradient',
            curveness: 0.5
          }
        }
      ]
    })
  );
});
```



## Key Points
- This is an official ECharts example from `sankey-energy/main.js`
- Template data format: `{ nodes: [{name: string, itemStyle?: {}}, ...], links: [{source: string, target: string, value: number}, ...] }`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
