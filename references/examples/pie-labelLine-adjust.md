# 饼图引导线调整 / Label Line Adjust

**Category:** `pie`
**Example dir:** `pie-labelLine-adjust`
**Difficulty:** 3

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
var datas = [
  ////////////////////////////////////////
  [
    { name: '圣彼得堡来客', value: 5.6 },
    { name: '陀思妥耶夫斯基全集', value: 1 },
    { name: '史记精注全译（全6册）', value: 0.8 },
    { name: '加德纳艺术通史', value: 0.5 },
    { name: '表象与本质', value: 0.5 },
    { name: '其它', value: 3.8 }
  ],
  // ////////////////////////////////////////
  [
    { name: '银河帝国5：迈向基地', value: 3.8 },
    { name: '俞军产品方法论', value: 2.3 },
    { name: '艺术的逃难', value: 2.2 },
    { name: '第一次世界大战回忆录（全五卷）', value: 1.3 },
    { name: 'Scrum 精髓', value: 1.2 },
    { name: '其它', value: 5.7 }
  ],
  ////////////////////////////////////////
  [
    { name: '克莱因壶', value: 3.5 },
    { name: '投资最重要的事', value: 2.8 },
    { name: '简读中国史', value: 1.7 },
    { name: '你当像鸟飞往你的山', value: 1.4 },
    { name: '表象与本质', value: 0.5 },
    { name: '其它', value: 3.8 }
  ]
];
option = {
  title: {
    text: '阅读书籍分布',
    left: 'center',
    textStyle: {
      color: '#999',
      fontWeight: 'normal',
      fontSize: 14
    }
  },
  series: datas.map(function (data, idx) {
    var top = idx * 33.3;
    return {
      type: 'pie',
      radius: [20, 60],
      top: top + '%',
      height: '33.33%',
      left: 'center',
      width: 400,
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 1
      },
      label: {
        alignTo: 'edge',
        formatter: '{name|{b}}\n{time|{c} 小时}',
        minMargin: 5,
        edgeDistance: 10,
        lineHeight: 15,
        rich: {
          time: {
            fontSize: 10,
            color: '#999'
          }
        }
      },
      labelLine: {
        length: 15,
        length2: 0,
        maxSurfaceAngle: 80
      },
      labelLayout: function (params) {
        const isLeft = params.labelRect.x < myChart.getWidth() / 2;
        const points = params.labelLinePoints;
        // Update the end point.
        points[2][0] = isLeft
          ? params.labelRect.x
          : params.labelRect.x + params.labelRect.width;
        return {
          labelLinePoints: points
        };
      },
      data: data
    };
  })
};
```

## Relevant Debug Patterns
## #17
 — Pie 模板 roseType/RADIUS 类型错误导致空白
- **日期**：2026-06-13
- **现象**：09_Pie_Basic 空白，无任何图表
- **根因**：(1) `ROSE_TYPE: ""` → JS 中变成 `roseType: ''`（空字符串），ECharts 不接受空串，只接受 `false`/`'radius'`/`'area'`；(2) `RADIUS: "['40%','70%']"` 被 `_json_safe` 当作字符串处理，单引号 JSON 解析失败，输出为带转义的字符串而非数组
- **修复**：(1) `ROSE_TYPE: "false"` → `_json_safe` 识别为 JS keyword，输出 `false`；(2) `RADIUS` 改为 Python list `["40%","70%"]` → `_json_safe` 用 `json.dumps` 正确序列化为 JS 数组 `["40%","70%"]`；(3) **模板 `pie/basic.html` 增加防御**：`roseType` 默认为 `...

## #21
 — Sunburst 空白：RADIUS 字符串 + FOCUS 值非法
- **日期**：2026-06-13
- **现象**：20_Sunburst 一片空白
- **根因**：(1) `RADIUS: "['0%','90%']"` — 字符串假数组，同 #17 pie 的问题，`_json_safe` 将其当作字符串处理；(2) `FOCUS: "none"` — ECharts sunburst `emphasis.focus` 只接受 `'ancestor'` 或 `'descendant'`，不接受 `'none'`
- **修复**：(1) `RADIUS` 改为 `D(["0%","90%"])` — JSON 数组；(2) `FOCUS: "ancestor"`；(3) **模板增加防御**：`radius: {{RADIUS}} || ["0%","90%"]` 和 `focus: {{FOCUS}} || "ancestor"`

---
...

## Key Points
- This is an official ECharts example from `pie-labelLine-adjust/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
