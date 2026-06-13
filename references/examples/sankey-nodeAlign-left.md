# 桑基图左对齐布局 / Node Align Left in Sankey

**Category:** `sankey`
**Example dir:** `sankey-nodeAlign-left`

## Template
- **sankey/basic.html** — Sankey
Data format: `{ nodes: [{name: string, itemStyle?: {}}, ...], links: [{source: string, target: string, value: number}, ...] }`

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
- Generate via: `scripts/build_template.py sankey/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
