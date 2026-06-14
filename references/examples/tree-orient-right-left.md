# tree-orient-right-left

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=tree-orient-right-left

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

**1 data arrays** to replace:
- `data[0]`: `data: [data]`

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: From Right to Left Tree
category: tree
titleCN: 从右到左树状图
*/
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

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
