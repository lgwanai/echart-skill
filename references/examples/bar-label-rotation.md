# bar-label-rotation

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-label-rotation
**Chart Type:** `bar`

## ⚠️ CLEANED FOR STANDALONE — app.config inlined

## User Data Requirements
Columns needed: need **category** + **value** columns (4 series recommended)

## Data Arrays — Complete Replacement Guide

**6 array(s)** to replace with real data:

### [0] `data` (context: legend)
```
data: ['Forest', 'Steppe', 'Desert', 'Wetland']
```

### [1] `data` (context: xAxis)
```
data: ['2012', '2013', '2014', '2015', '2016']
```

### [2] `data` (context: series)
```
data: [320, 332, 301, 334, 390]
```

### [3] `data` (context: root)
```
data: [220, 182, 191, 234, 290]
```

### [4] `data` (context: root)
```
data: [150, 232, 201, 154, 190]
```

### [5] `data` (context: root)
```
data: [98, 77, 101, 99, 40]
```

## Agent Workflow
1. Query DuckDB for 4 numeric columns
2. LEGEND = JSON array of series names
3. CATEGORIES = JSON array of x-axis labels
4. SERIES = JSON array of `{name, type:'bar', barGap:0, label:{...}, emphasis:{focus:'series'}, data:[...]}`
5. Use build_template.py → fill {{PLACEHOLDER}} → validate_chart.py
