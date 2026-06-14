# 双数值轴折线图

**Category:** `line`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=line-in-cartesian-coordinate-system
**Template:** examples/line-in-cartesian-coordinate-system.html
**Data Format:** `[[x, y], [x, y], ...]`

## Official Option Code

```javascript
/*
title: Line Chart in Cartesian Coordinate System
category: line
titleCN: 双数值轴折线图
difficulty: 7
*/
option = {
  xAxis: {},
  yAxis: {},
  series: [
    {
      data: [
        [10, 40],
        [50, 100],
        [40, 20]
      ],
      type: 'line'
    }
  ]
};
```

## Placeholders

| Placeholder | Type | Description |
|-------------|------|-------------|
| `{{{TITLE}}}` | string | title |

## Usage
- Build: `scripts/build_template.py examples/line-in-cartesian-coordinate-system.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
