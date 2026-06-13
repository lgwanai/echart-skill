# 径向树状图 / Radial Tree

**Category:** `tree`
**Example dir:** `tree-radial`

## Template
- **tree/basic.html** — Tree
Data format: `[{name: string, value?: number, collapsed?: boolean, children?: [...]}]`

## Option Code
```javascript
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/data/flare.json', function (data) {
  myChart.hideLoading();
  myChart.setOption(
    (option = {
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove'
      },
      series: [
        {
          type: 'tree',
          data: [data],
          top: '18%',
          bottom: '14%',
          layout: 'radial',
          symbol: 'emptyCircle',
          symbolSize: 7,
          initialTreeDepth: 3,
          animationDurationUpdate: 750,
          emphasis: {
            focus: 'descendant'
          }
        }
      ]
    })
  );
});
```

## Key Points
- Generate via: `scripts/build_template.py tree/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
