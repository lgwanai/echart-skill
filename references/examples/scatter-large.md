# scatter-large

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-large
**Chart Type:** `inside`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

## Reference Code

```javascript
/*
title: Large Scatter
category: scatter
titleCN: 大规模散点图
difficulty: 5
*/
function genData(len, offset) {
  let arr = new Float32Array(len * 2);
  let off = 0;
  for (let i = 0; i < len; i++) {
    let x = +Math.random() * 10;
    let y =
      +Math.sin(x) -
      x * (len % 2 ? 0.1 : -0.1) * Math.random() +
      (offset || 0) / 10;
    arr[off++] = x;
    arr[off++] = y;
  }
  return arr;
}
const data1 = genData(5e5);
const data2 = genData(5e5, 10);
option = {
  title: {
    text:
      echarts.format.addCommas(data1.length / 2 + data2.length / 2) + ' Points'
  },
  tooltip: {},
  toolbox: {
    left: 'center',
    feature: {
      dataZoom: {}
    }
  },
  legend: {
    orient: 'vertical',
    right: 10
  },
  xAxis: [{}],
  yAxis: [{}],
  dataZoom: [
    {
      type: 'inside'
    },
    {
      type: 'slider'
    }
  ],
  animation: false,
  series: [
    {
      name: 'A',
      type: 'scatter',
      data: data1,
      dimensions: ['x', 'y'],
      symbolSize: 3,
      itemStyle: {
        opacity: 0.4
      },
      large: true
    },
    {
      name: 'B',
      type: 'scatter',
      data: data2,
      dimensions: ['x', 'y'],
      symbolSize: 3,
      itemStyle: {
        opacity: 0.4
      },
      large: true
    }
  ]
};
```
