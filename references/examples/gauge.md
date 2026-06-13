# 基础仪表盘

**Category:** `gauge`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=gauge
**Template:** NONE — use knowledge base
**Data Format:** `N/A`

## Official Option Code

```javascript
/*
title: Gauge Basic chart
titleCN: 基础仪表盘
category: gauge
difficulty: 1
*/
option = {
  tooltip: {
    formatter: '{a} <br/>{b} : {c}%'
  },
  series: [
    {
      name: 'Pressure',
      type: 'gauge',
      detail: {
        formatter: '{value}'
      },
      data: [
        {
          value: 50,
          name: 'SCORE'
        }
      ]
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
