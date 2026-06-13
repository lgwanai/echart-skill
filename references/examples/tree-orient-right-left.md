# 从右到左树状图 / From Right to Left Tree

**Category:** `tree`
**Example dir:** `tree-orient-right-left`

## Template
- **tree/basic.html** — Tree
Data format: `[{name: string, value?: number, collapsed?: boolean, children?: [...]}]`

## Option Code
```javascript
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/data/flare.json', function (data) {
  myChart.hideLoading();
  data.children.forEach(function (datum, index) {
    index % 2 === 0 && (datum.collapsed = true);
  });
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
          top: '1%',
          left: '15%',
          bottom: '1%',
          right: '7%',
          symbolSize: 7,
          orient: 'RL',
          label: {
            position: 'right',
            verticalAlign: 'middle',
            align: 'left'
          },
          leaves: {
            label: {
              position: 'left',
              verticalAlign: 'middle',
              align: 'right'
            }
          },
          emphasis: {
            focus: 'descendant'
          },
          expandAndCollapse: true,
          animationDuration: 550,
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
