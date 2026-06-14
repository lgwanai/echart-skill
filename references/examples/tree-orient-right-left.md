# tree-orient-right-left

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=tree-orient-right-left
**Chart Type:** `tree`

## User Data Requirements

Columns needed: need nested **name+children** tree structure

## Data Arrays — Replacement Guide

The code contains **1 data array(s)** to replace:

### data[0]: `series[0]`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [data]`
- **Replace with**: real data from DuckDB in the same format


## External Data Format

This example uses external data. Format from `flare.json`:

```json
[
  {
    "name": "analytics",
    "children": [
      {
        "name": "cluster",
        "children": [
          {
            "name": "AgglomerativeCluster",
            "value": 3938
          },
          {
            "name": "CommunityStructure",
            "value": 3812
          },
          {
            "name": "HierarchicalCluster",
            "value": 6714
          },
          {
            "name": "MergeEdge",
            "value": 743
          }
        ]
      },
      {
   
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
