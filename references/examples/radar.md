# 基础雷达图

**Category:** `radar`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=radar
**Template:** radar/basic.html
**Data Format:** `{ indicators: [{name: string, max: number}, ...], series: [{name: string, value: number[]}, ...] }`

## Official Option Code

```javascript
/*
title: Basic Radar Chart
category: radar
titleCN: 基础雷达图
difficulty: 0
*/
option = {
  title: {
    text: 'Basic Radar Chart'
  },
  legend: {
    data: ['Allocated Budget', 'Actual Spending']
  },
  radar: {
    // shape: 'circle',
    indicator: [
      { name: 'Sales', max: 6500 },
      { name: 'Administration', max: 16000 },
      { name: 'Information Technology', max: 30000 },
      { name: 'Customer Support', max: 38000 },
      { name: 'Development', max: 52000 },
      { name: 'Marketing', max: 25000 }
    ]
  },
  series: [
    {
      name: 'Budget vs spending',
      type: 'radar',
      data: [
        {
          value: [4200, 3000, 20000, 35000, 50000, 18000],
          name: 'Allocated Budget'
        },
        {
          value: [5000, 14000, 28000, 26000, 42000, 21000],
          name: 'Actual Spending'
        }
      ]
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py radar/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
