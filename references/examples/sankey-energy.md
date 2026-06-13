# 桑基图渐变色边 / Gradient Edge

**Category:** `sankey`
**Example dir:** `sankey-energy`

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
- Generate via: `scripts/build_template.py sankey/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
