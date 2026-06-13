# 堆叠柱状图的归一化

**Category:** `bar`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-stack-normalization
**Template:** examples/bar-stack-normalization.html
**Data Format:** `{ categories: string[], series: [{name: string, stack: string, data: number[]}, ...] }`
**Features:** labels displayed

## Official Option Code

```javascript
/*
title: Stacked Bar Normalization
titleCN: 堆叠柱状图的归一化
category: bar
difficulty: 3
*/
// There should not be negative values in rawData
const rawData = [
  [100, 302, 301, 334, 390, 330, 320],
  [320, 132, 101, 134, 90, 230, 210],
  [220, 182, 191, 234, 290, 330, 310],
  [150, 212, 201, 154, 190, 330, 410],
  [820, 832, 901, 934, 1290, 1330, 1320]
];
const totalData = [];
for (let i = 0; i < rawData[0].length; ++i) {
  let sum = 0;
  for (let j = 0; j < rawData.length; ++j) {
    sum += rawData[j][i];
  }
  totalData.push(sum);
}
const series = [
  'Direct',
  'Mail Ad',
  'Affiliate Ad',
  'Video Ad',
  'Search Engine'
].map((name, sid) => {
  return {
    name,
    type: 'bar',
    stack: 'total',
    barWidth: '60%',
    label: {
      show: true,
      formatter: (params) => Math.round(params.value * 1000) / 10 + '%'
    },
    data: rawData[sid].map((d, did) =>
      totalData[did] <= 0 ? 0 : d / totalData[did]
    )
  };
});
option = {
  legend: {
    selectedMode: false
  },
  yAxis: {
    type: 'value'
  },
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  series
};
```

## Usage
- Build: `scripts/build_template.py examples/bar-stack-normalization.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
