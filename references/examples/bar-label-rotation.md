# bar-label-rotation

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-label-rotation
**Chart Type:** `bar`

## ⚠️ CLEANED FOR STANDALONE — app.config inlined

## User Data Requirements
Columns needed: need **category** + **value** columns (4 series recommended)

## Data Arrays — Replacement Guide

The code contains **5 data array(s)** — replace ALL with real data:

### data[0]: `legend`
- **Format**: `['name1','name2',...]` — legend labels (string array, matches series names)
- **Replace with**: real series names from DuckDB

### data[1]: `xAxis`
- **Format**: `['cat1','cat2',...]` — x-axis category labels (string array)
- **Replace with**: real category labels from DuckDB

### data[2-5]: `series[0-3].data`
- **Format**: `[n1,n2,...]` — flat numeric value array
- **Replace with**: real numeric values from DuckDB

## Clean Code (app.config references removed)

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
1. Query DuckDB for 4 numeric columns
2. LEGEND = JSON array of series names
3. CATEGORIES = JSON array of x-axis labels
4. SERIES = JSON array of `{name, type:'bar', barGap:0, label:{...}, emphasis:{focus:'series'}, data:[...]}`
5. Use build_template.py → fill {{PLACEHOLDER}} → validate_chart.py
