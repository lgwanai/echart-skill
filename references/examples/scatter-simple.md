# 基础散点图

**Category:** `scatter`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-simple
**Template:** scatter/basic.html
**Data Format:** `[[x, y], [x, y], ...]`

## Official Option Code

```javascript
/*
title: Basic Scatter Chart
category: scatter
titleCN: 基础散点图
difficulty: 0
*/
option = {
  xAxis: {},
  yAxis: {},
  series: [
    {
      symbolSize: 20,
      data: [
        [10.0, 8.04],
        [8.07, 6.95],
        [13.0, 7.58],
        [9.05, 8.81],
        [11.0, 8.33],
        [14.0, 7.66],
        [13.4, 6.81],
        [10.0, 6.33],
        [14.0, 8.96],
        [12.5, 6.82],
        [9.15, 7.2],
        [11.5, 7.2],
        [3.03, 4.23],
        [12.2, 7.83],
        [2.02, 4.47],
        [1.05, 3.33],
        [4.05, 4.96],
        [6.03, 7.24],
        [12.0, 6.26],
        [12.0, 8.84],
        [7.08, 5.82],
        [5.02, 5.68]
      ],
      type: 'scatter'
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py scatter/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
