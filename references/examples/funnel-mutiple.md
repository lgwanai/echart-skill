# funnel-mutiple

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=funnel-mutiple
**Chart Type:** `funnel`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: need **stage** + **count** columns
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

Data arrays to replace: **5**

## Reference Code

```javascript
/*
title: Multiple Funnels
category: funnel
titleCN: 多漏斗图
*/
option = {
  title: {
    text: 'Funnel',
    left: 'left',
    top: 'bottom'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b} : {c}%'
  },
  toolbox: {
    orient: 'vertical',
    top: 'center',
    feature: {
      dataView: { readOnly: false },
      restore: {},
      saveAsImage: {}
    }
  },
  legend: {
    orient: 'vertical',
    left: 'left',
    data: ['Show', 'Click', 'Visit', 'Inquiry', 'Order']
  },
  series: [
    {
      name: 'Funnel',
      type: 'funnel',
      width: '40%',
      height: '45%',
      left: '5%',
      top: '50%',
      data: [
        { value: 60, name: 'Visit' },
        { value: 30, name: 'Inquiry' },
        { value: 10, name: 'Order' },
        { value: 80, name: 'Click' },
        { value: 100, name: 'Show' }
      ]
    },
    {
      name: 'Pyramid',
      type: 'funnel',
      width: '40%',
      height: '45%',
      left: '5%',
      top: '5%',
      sort: 'ascending',
      data: [
        { value: 60, name: 'Visit' },
        { value: 30, name: 'Inquiry' },
        { value: 10, name: 'Order' },
        { value: 80, name: 'Click' },
        { value: 100, name: 'Show' }
      ]
    },
    {
      name: 'Funnel',
      type: 'funnel',
      width: '40%',
      height: '45%',
      left: '55%',
      top: '5%',
      label: {
        position: 'left'
      },
      data: [
        { value: 60, name: 'Visit' },
        { value: 30, name: 'Inquiry' },
        { value: 10, name: 'Order' },
        { value: 80, name: 'Click' },
        { value: 100, name: 'Show' }
      ]
    },
    {
      name: 'Pyramid',
      type: 'funnel',
      width: '40%',
      height: '45%',
      left: '55%',
      top: '50%',
      sort: 'ascending',
      label: {
        position: 'left'
      },
      data: [
        { value: 60, name: 'Visit' },
        { value: 30, name: 'Inquiry' },
        { value: 10, name: 'Order' },
        { value: 80, name: 'Click' },
        { value: 100, name: 'Show' }
      ]
    }
  ]
};
```
