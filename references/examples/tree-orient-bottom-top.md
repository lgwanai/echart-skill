# tree-orient-bottom-top

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=tree-orient-bottom-top
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
title: From Bottom to Top Tree
category: tree
titleCN: 从下到上树状图
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
