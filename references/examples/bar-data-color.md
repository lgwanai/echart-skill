# 自定义单个柱子颜色

**Category:** `bar`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-data-color
**Template:** examples/bar-data-color.html
**Data Format:** `{ categories: string[], values: number[] }`
**Features:** per-item colors via itemStyle

## Official Option Code

```javascript
/*
title: Set Style of Single Bar.
category: bar
titleCN: 自定义单个柱子颜色
difficulty: 1
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
      data: [
        120,
        {
          value: 200,
          itemStyle: {
            color: '#505372'
          }
        },
        150,
        80,
        70,
        110,
        130
      ],
      type: 'bar'
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py examples/bar-data-color.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
