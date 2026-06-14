# bar-label-rotation

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-label-rotation
**Chart Type:** `bar`

## ⚠️ CLEANED FOR STANDALONE — app.config values inlined

## Data Arrays — Complete Replacement Guide

This chart has **3 placeholders** (not individual data arrays). Use `build_template.py`.

| Placeholder | Context | Format | Example |
|-------------|---------|--------|---------|
| `{{LEGEND}}` | legend data | string array | `["Email","Ads","Video","Direct"]` |
| `{{CATEGORIES}}` | xAxis data | string array | `["Mon","Tue","Wed","Thu","Fri"]` |
| `{{SERIES}}` | series array | object array with nested data | see below |

### SERIES format
```json
[{
  "name": "Email",
  "type": "bar",
  "barGap": 0,
  "label": {
    "show": true, "position": "insideBottom", "distance": 15,
    "align": "left", "verticalAlign": "middle", "rotate": 90,
    "formatter": "{c}  {name|{a}}", "fontSize": 16, "rich": {"name": {}}
  },
  "emphasis": {"focus": "series"},
  "data": [120, 132, 101, 134, 90]
}]
```

## Clean Code (ready for build_template.py)

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
1. Query DuckDB for 4 numeric columns + category labels
2. Build LEGEND, CATEGORIES, SERIES JSON
3. `build_template.py examples/bar-label-rotation.html` → fill placeholders
4. `validate_chart.py` → verify
