# 从上到下树状图 / From Top to Bottom Tree

**Category:** `tree`
**Example dir:** `tree-vertical`

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
          top: '8%',
          bottom: '20%',
          symbol: 'emptyCircle',
          orient: 'vertical',
          expandAndCollapse: true,
          label: {
            position: 'top',
            rotate: -90,
            verticalAlign: 'middle',
            align: 'right',
            fontSize: 9
          },
          leaves: {
            label: {
              position: 'bottom',
              rotate: -90,
              verticalAlign: 'middle',
              align: 'left'
            }
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
