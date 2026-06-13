# 径向树状图

**Category:** `tree`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=tree-radial
**Template:** tree/basic.html
**Data Format:** `[{name: string, value?: number, collapsed?: boolean, children?: [...]}]`
**Features:** emphasis/hover effects

## Official Option Code

```javascript
/*
title: Radial Tree
category: tree
titleCN: 径向树状图
*/
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

## Usage
- Build: `scripts/build_template.py tree/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
