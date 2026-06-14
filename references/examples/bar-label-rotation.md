# 柱状图标签旋转 / Bar Label Rotation

**Category:** `bar`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-label-rotation
**Template:** examples/bar-label-rotation.html

## Placeholders

| Placeholder | Type | Format | Example |
|-------------|------|--------|---------|
| `{{TITLE}}` | string | 图表标题 | `"bar-label-rotation"` |
| `{{LEGEND}}` | JSON array | 系列名称列表，与 SERIES 中 name 一一对应 | `["Email","Ads","Video","Direct"]` |
| `{{CATEGORIES}}` | JSON array | X 轴分类标签 | `["Mon","Tue","Wed","Thu","Fri"]` |
| `{{SERIES}}` | JSON array | 系列对象数组，每个包含 name/type/data/label | 见下方 |

### SERIES 格式
```json
[{
  "name": "Email",
  "type": "bar",
  "barGap": 0,
  "label": {
    "show": true, "position": "insideBottom", "distance": 15,
    "align": "left", "verticalAlign": "middle", "rotate": 90,
    "formatter": "{c}  {name|{a}}", "fontSize": 16,
    "rich": {"name": {}}
  },
  "emphasis": {"focus": "series"},
  "data": [120, 132, 101, 134, 90]
}]
```

## Agent Workflow
1. DuckDB 查询 4 列数据 → 构建 SERIES 数组
2. LEGEND = 系列名称数组
3. CATEGORIES = X 轴标签
4. `build_template.py` 填充 → `validate_chart.py` 校验

## Official Option Code (reference)
```javascript
option = {
  tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
  legend: { data: ["Forest","Steppe","Desert","Wetland"] },
  toolbox: { show: true, orient: "vertical", left: "right", top: "center",
    feature: { mark: { show: true }, dataView: { show: true, readOnly: false },
      magicType: { show: true, type: ["line","bar","stack"] },
      restore: { show: true }, saveAsImage: { show: true } } },
  xAxis: [{ type: "category", axisTick: { show: false }, data: ["2012","2013","2014","2015","2016"] }],
  yAxis: [{ type: "value" }],
  series: [
    { name: "Forest", type: "bar", barGap: 0, label: labelOption, emphasis: { focus: "series" }, data: [320,332,301,334,390] },
    { name: "Steppe", type: "bar", label: labelOption, emphasis: { focus: "series" }, data: [220,182,191,234,290] },
    { name: "Desert", type: "bar", label: labelOption, emphasis: { focus: "series" }, data: [150,232,201,154,190] },
    { name: "Wetland", type: "bar", label: labelOption, emphasis: { focus: "series" }, data: [98,77,101,99,40] }
  ]
};
```
