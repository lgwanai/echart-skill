# sankey-nodeAlign-left

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sankey-nodeAlign-left
**Chart Type:** `sankey`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: need **source**, **target**, **value** columns
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

## Reference Code

```javascript
/*
title: Node Align Left in Sankey
category: sankey
titleCN: 桑基图左对齐布局
difficulty: 3
*/
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/data/energy.json', function (data) {
  myChart.hideLoading();
  myChart.setOption(
    (option = {
      title: {
        text: 'Node Align Left'
      },
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove'
      },
      series: [
        {
          type: 'sankey',
          emphasis: {
            focus: 'adjacency'
          },
          nodeAlign: 'left',
          data: data.nodes,
          links: data.links,
          lineStyle: {
            color: 'source',
            curveness: 0.5
          }
        }
      ]
    })
  );
});
```
