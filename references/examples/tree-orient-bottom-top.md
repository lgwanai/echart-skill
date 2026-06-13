# 从下到上树状图 / From Bottom to Top Tree

**Category:** `tree`
**Example dir:** `tree-orient-bottom-top`

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
          left: '2%',
          right: '2%',
          top: '20%',
          bottom: '8%',
          symbol: 'emptyCircle',
          orient: 'BT',
          expandAndCollapse: true,
          label: {
            position: 'bottom',
            rotate: 90,
            verticalAlign: 'middle',
            align: 'right'
          },
          leaves: {
            label: {
              position: 'top',
              rotate: 90,
              verticalAlign: 'middle',
              align: 'left'
            }
          },
          emphasis: {
            focus: 'descendant'
          },
          animationDurationUpdate: 750
        }
      ]
    })
  );
});
```

## Key Points
- Generate via: `scripts/build_template.py tree/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
