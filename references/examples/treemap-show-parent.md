# treemap-show-parent

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=treemap-show-parent
**Chart Type:** `treemap`

## User Data Requirements

Columns needed: need nested **name+value** or **name+children**

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `disk.tree.json`:

```json
[
  {
    "value": 40,
    "name": "Accessibility",
    "path": "Accessibility"
  },
  {
    "value": 180,
    "name": "Accounts",
    "path": "Accounts",
    "children": [
      {
        "value": 76,
        "name": "Access",
        "path": "Accounts/Access",
        "children": [
          {
            "value": 12,
            "name": "DefaultAccessPlugin.bundle",
            "path": "Accounts/Access/DefaultAccessPlugin.bundle"
          },
          {
            "value": 28,
            "
...
```

Agent: build DuckDB query to produce matching data structure.
## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Show Parent Labels
category: treemap
titleCN: 显示父层级标签
*/
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/data/disk.tree.json', function (diskData) {
  myChart.hideLoading();
  function getLevelOption() {
    return [
      {
        itemStyle: {
          borderColor: '#777',
          borderWidth: 0,
          gapWidth: 1
        },
        upperLabel: {
          show: false
        }
      },
      {
        itemStyle: {
          borderColor: '#555',
          borderWidth: 5,
          gapWidth: 1
        },
        emphasis: {
          itemStyle: {
            borderColor: '#ddd'
          }
        }
      },
      {
        colorSaturation: [0.35, 0.5],
        itemStyle: {
          borderWidth: 5,
          gapWidth: 1,
          borderColorSaturation: 0.6
        }
      }
    ];
  }
  myChart.setOption(
    (option = {
      title: {
        text: 'Disk Usage',
        left: 'center'
      },
      tooltip: {
        formatter: function (info) {
          var value = info.value;
          var treePathInfo = info.treePathInfo;
          var treePath = [];
          for (var i = 1; i < treePathInfo.length; i++) {
            treePath.push(treePathInfo[i].name);
          }
          return [
            '<div class="tooltip-title">' +
              echarts.format.encodeHTML(treePath.join('/')) +
              '</div>',
            'Disk Usage: ' + echarts.format.addCommas(value) + ' KB'
          ].join('');
        }
      },
      series: [
        {
          name: 'Disk Usage',
          type: 'treemap',
          visibleMin: 300,
          label: {
            show: true,
            formatter: '{b}'
          },
          upperLabel: {
            show: true,
            height: 30
          },
          itemStyle: {
            borderColor: '#fff'
          },
          levels: getLevelOption(),
          data: diskData
        }
      ]
    })
  );
});
```
