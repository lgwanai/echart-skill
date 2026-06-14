# 基础面积图

**Category:** `line`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=area-basic
**Template:** examples/area-basic.html
**Data Format:** `{ categories: string[], values: number[] }`
**Features:** area fill enabled

## Official Option Code

```javascript
/*
title: Basic area chart
titleCN: 基础面积图
category: line
difficulty: 1
*/
option = {
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [820, 932, 901, 934, 1290, 1330, 1320],
      type: 'line',
      areaStyle: {}
    }
  ]
};
```

## Placeholders

| Placeholder | Type | Description |
|-------------|------|-------------|
| `{{{TITLE}}}` | string | title |

## Usage
- Build: `scripts/build_template.py examples/area-basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
