# 带抖动的散点图

**Category:** `scatter`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-jitter
**Template:** examples/scatter-jitter.html
**Data Format:** `[[x, y], [x, y], ...]`
**Features:** per-item colors via itemStyle

## Official Option Code

```javascript
/*
title: Scatter with Jittering
category: scatter
titleCN: 带抖动的散点图
difficulty: 3
since: 6.0.0
*/
const grid = {
  left: 80,
  right: 50
};
const width = myChart.getWidth() - grid.left - grid.right;
const data = [];
for (let day = 0; day < 7; ++day) {
  for (let i = 0; i < 1000; ++i) {
    const y = Math.tan(i) / 2 + 7;
    data.push([day, y, Math.random()]);
  }
}
option = {
  title: {
    text: 'Scatter with Jittering'
  },
  grid,
  xAxis: {
    type: 'category',
    jitter: (width / 7) * 0.8,
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value',
    max: 10,
    min: 0
  },
  series: [
    {
      name: 'Sleeping Hours',
      type: 'scatter',
      data,
      colorBy: 'data',
      itemStyle: {
        opacity: 0.4
      }
    }
  ]
};
```

## Placeholders

| Placeholder | Type | Description |
|-------------|------|-------------|
| `{{{TITLE}}}` | string | title |

## Usage
- Build: `scripts/build_template.py examples/scatter-jitter.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
