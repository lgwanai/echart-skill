# sankey-energy

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sankey-energy
**Chart Type:** `sankey`

## User Data Requirements

Columns needed: need **source**, **target**, **value** columns

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `energy.json`:

```json
[
  {
    "name": "Agricultural 'waste'"
  },
  {
    "name": "Bio-conversion"
  },
  {
    "name": "Liquid"
  }
]
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
title: Gradient Edge
category: sankey
titleCN: 桑基图渐变色边
difficulty: 3
*/
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
