# 基础南丁格尔玫瑰图

**Category:** `pie`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=pie-roseType-simple
**Template:** examples/pie-roseType-simple.html
**Data Format:** `[{name: string, value: number}, ...]`

## Official Option Code

```javascript
/*
title: Nightingale Chart
category: pie
titleCN: 基础南丁格尔玫瑰图
shotWidth: 800
difficulty: 2
*/
option = {
  legend: {
    top: 'bottom'
  },
  toolbox: {
    show: true,
    feature: {
      mark: { show: true },
      dataView: { show: true, readOnly: false },
      restore: { show: true },
      saveAsImage: { show: true }
    }
  },
  series: [
    {
      name: 'Nightingale Chart',
      type: 'pie',
      radius: [50, 250],
      center: ['50%', '50%'],
      roseType: 'area',
      itemStyle: {
        borderRadius: 8
      },
      data: [
        { value: 40, name: 'rose 1' },
        { value: 38, name: 'rose 2' },
        { value: 32, name: 'rose 3' },
        { value: 30, name: 'rose 4' },
        { value: 28, name: 'rose 5' },
        { value: 26, name: 'rose 6' },
        { value: 22, name: 'rose 7' },
        { value: 18, name: 'rose 8' }
      ]
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py examples/pie-roseType-simple.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
