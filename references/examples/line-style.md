# 自定义折线图样式

**Category:** `line`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-style
**Template:** examples/line-style.html
**Data Format:** `{ categories: string[], values: number[] }`
**Features:** per-item colors via itemStyle

## Official Option Code

```javascript
/*
title: Line Style and Item Style
category: line
titleCN: 自定义折线图样式
difficulty: 6
*/
option = {
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [120, 200, 150, 80, 70, 110, 130],
      type: 'line',
      symbol: 'triangle',
      symbolSize: 20,
      lineStyle: {
        color: '#5470C6',
        width: 4,
        type: 'dashed'
      },
      itemStyle: {
        borderWidth: 3,
        borderColor: '#EE6666',
        color: 'yellow'
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
- Build: `scripts/build_template.py examples/line-style.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
