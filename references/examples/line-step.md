# 阶梯折线图 / Step Line

**Category:** `line`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-step
**Template:** examples/line-step.html
**Data Format:** `{values_start: [], values_middle: [], values_end: []}` — 3 series with different step values

## Official Option Code
```javascript
option = {
  title: { text: 'Step Line' },
  tooltip: { trigger: 'axis' },
  legend: { data: ['Step Start', 'Step Middle', 'Step End'] },
  xAxis: { type: 'category', data: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'] },
  yAxis: { type: 'value' },
  series: [
    { name: 'Step Start', type: 'line', step: 'start', data: [120,132,101,134,90,230,210] },
    { name: 'Step Middle', type: 'line', step: 'middle', data: [220,282,201,234,290,430,410] },
    { name: 'Step End', type: 'line', step: 'end', data: [450,432,401,454,590,530,510] }
  ]
};
```

## Key Points
- Requires **3 separate series** with step: 'start'/'middle'/'end'
- Template: `examples/line-step.html` (NOT line/basic.html)
- Build: `scripts/build_template.py line/step.html -d data.json`
