# 从上到下树状图 / From Top to Bottom Tree

**Category:** `tree`
**Example dir:** `tree-vertical`
**Difficulty:** 

## Template Match
- **tree/basic.html** — Tree

## Option Code
```javascript
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/data/flare.json', function (data) {
  myChart.hideLoading();
  myChart.setOption(
    (option = {
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove'
      },
      series: [
        {
          type: 'tree',
          data: [data],
          left: '2%',
          right: '2%',
          top: '8%',
          bottom: '20%',
          symbol: 'emptyCircle',
          orient: 'vertical',
          expandAndCollapse: true,
          label: {
            position: 'top',
            rotate: -90,
            verticalAlign: 'middle',
            align: 'right',
            fontSize: 9
          },
          leaves: {
            label: {
              position: 'bottom',
              rotate: -90,
              verticalAlign: 'middle',
              align: 'left'
            }
          },
          animationDurationUpdate: 750
        }
      ]
    })
  );
});
```

## Relevant Debug Patterns
## #20
 — Treemap 父节点缺少 value 导致布局错误
- **日期**：2026-06-13
- **现象**：19_Treemap 布局比例失调，标签只显示根节点名称
- **根因**：(1) 父节点没有 `value` 属性，ECharts treemap 无法按比例分配面积；(2) 数据只有 2 大类 4 项，过于稀疏；(3) `UPPER_LABEL_SHOW: false` 导致上层标签不显示
- **修复**：(1) 父节点添加 `value`（子节点之和）；(2) 扩充为 3 大类 11 项；(3) `UPPER_LABEL_SHOW: true`；(4) **模板增加防御**：`upperLabel.show` 和 `breadcrumb.show` 在值为空时默认为 `true`

---
...

## #22
 — Tree 空白：DATA 是对象而非数组
- **日期**：2026-06-13
- **现象**：23_Tree 一片空白
- **根因**：ECharts tree 的 `data` 必须是数组 `[{root}]`，但传入的是单个对象 `{name:"CEO",...}`
- **修复**：(1) DATA 改为 `D([{...}])` — 包裹在数组中；(2) **模板增加防御**：`data: [].concat({{DATA}})` — `[].concat(obj)` 自动包数组，`[].concat(arr)` 保持不变

---
...

## Key Points
- This is an official ECharts example from `tree-vertical/main.js`
- Template data format: `[{name: string, value?: number, collapsed?: boolean, children?: [...]}]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
