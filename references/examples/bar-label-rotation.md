# bar-label-rotation

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-label-rotation
**Chart Type:** `bar`

## Clean Standalone Code

All `app.config.*` replaced with actual values. Uses {{PLACEHOLDER}} for reliable data injection.

```javascript
const posList = ['left','right','top','bottom','inside','insideTop','insideLeft','insideRight','insideBottom','insideTopLeft','insideTopRight','insideBottomLeft','insideBottomRight'];

const labelOption = { show: true, position: 'insideBottom', distance: 15, align: 'left', verticalAlign: 'middle', rotate: 90, formatter: '{c}  {name|{a}}', fontSize: 16, rich: { name: {} } };

option = {
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { data: {{LEGEND}} },
  toolbox: { show: true, orient: 'vertical', left: 'right', top: 'center',
    feature: { mark: { show: true }, dataView: { show: true, readOnly: false },
      magicType: { show: true, type: ['line','bar','stack'] },
      restore: { show: true }, saveAsImage: { show: true } } },
  xAxis: [{ type: 'category', axisTick: { show: false }, data: {{CATEGORIES}} }],
  yAxis: [{ type: 'value' }],
  series: {{SERIES}}
};
```

## Agent Workflow
1. Query DuckDB for multiple series data
2. LEGEND = JSON array of series names
3. CATEGORIES = JSON array of x-axis labels  
4. SERIES = JSON array of series objects with labelOption inlined
5. Use build_template.py to fill {{PLACEHOLDER}} → validate_chart.py
