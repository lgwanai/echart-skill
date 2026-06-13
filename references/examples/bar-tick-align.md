# 坐标轴刻度与标签对齐

**Category:** `bar`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-tick-align
**Template:** examples/bar-tick-align.html
**Data Format:** `{ categories: string[], values: number[] }`

## Official Option Code

```javascript
/*
title: Axis Align with Tick
titleCN: 坐标轴刻度与标签对齐
category: bar
difficulty: 0
*/
option = {
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: [
    {
      type: 'category',
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      axisTick: {
        alignWithLabel: true
      }
    }
  ],
  yAxis: [
    {
      type: 'value'
    }
  ],
  series: [
    {
      name: 'Direct',
      type: 'bar',
      barWidth: '60%',
      data: [10, 52, 200, 334, 390, 330, 220]
    }
  ]
};
```

## Usage
- Build: `scripts/build_template.py examples/bar-tick-align.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
