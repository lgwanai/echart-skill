# line-y-category

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-y-category
**Chart Type:** `value`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

Data arrays to replace: **3**

## Reference Code

```javascript
/*
title: Line Y Category
category: line
titleCN: 垂直折线图（Y轴为类目轴）
difficulty: 8
*/
option = {
  legend: {
    data: ['Altitude (km) vs. temperature (°C)']
  },
  tooltip: {
    trigger: 'axis',
    formatter: 'Temperature : <br/>{b}km : {c}°C'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    axisLabel: {
      formatter: '{value} °C'
    }
  },
  yAxis: {
    type: 'category',
    axisLine: { onZero: false },
    axisLabel: {
      formatter: '{value} km'
    },
    boundaryGap: false,
    data: ['0', '10', '20', '30', '40', '50', '60', '70', '80']
  },
  series: [
    {
      name: 'Altitude (km) vs. temperature (°C)',
      type: 'line',
      symbolSize: 10,
      symbol: 'circle',
      smooth: true,
      lineStyle: {
        width: 3,
        shadowColor: 'rgba(0,0,0,0.3)',
        shadowBlur: 10,
        shadowOffsetY: 8
      },
      data: [15, -50, -56.5, -46.5, -22.1, -2.5, -27.7, -55.7, -76.5]
    }
  ]
};
```
