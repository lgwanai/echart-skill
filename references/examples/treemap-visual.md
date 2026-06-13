# 映射为渐变色 / Gradient Mapping

**Category:** `treemap`
**Example dir:** `treemap-visual`
**Difficulty:** 

## Template Match
- **tree/basic.html** — Tree

## Option Code
```javascript
myChart.showLoading();
const household_america_2012 = 113616229;
$.get(
  ROOT_PATH + '/data/asset/data/obama_budget_proposal_2012.json',
  function (obama_budget_2012) {
    myChart.hideLoading();
    const visualMin = -100;
    const visualMax = 100;
    const visualMinBound = -40;
    const visualMaxBound = 40;
    convertData(obama_budget_2012);
    function convertData(originList) {
      let min = Infinity;
      let max = -Infinity;
      for (let i = 0; i < originList.length; i++) {
        let node = originList[i];
        if (node) {
          let value = node.value;
          value[2] != null && value[2] < min && (min = value[2]);
          value[2] != null && value[2] > max && (max = value[2]);
        }
      }
      for (let i = 0; i < originList.length; i++) {
        let node = originList[i];
        if (node) {
          let value = node.value;
          // Scale value for visual effect
          if (value[2] != null && value[2] > 0) {
            value[3] = echarts.number.linearMap(
              value[2],
              [0, max],
              [visualMaxBound, visualMax],
              true
            );
          } else if (value[2] != null && value[2] < 0) {
            value[3] = echarts.number.linearMap(
              value[2],
              [min, 0],
              [visualMin, visualMinBound],
              true
            );
          } else {
            value[3] = 0;
          }
          if (!isFinite(value[3])) {
            value[3] = 0;
          }
          if (node.children) {
            convertData(node.children);
          }
        }
      }
    }
    function isValidNumber(num) {
      return num != null && isFinite(num);
    }
    myChart.setOption(
      (option = {
        title: {
          left: 'center',
          text: 'Gradient Mapping',
          subtext: 'Growth > 0: green; Growth < 0: red; Growth = 0: grey'
        },
        tooltip: {
          formatter: function (info) {
            let value = info.value;
            let amount = value[0];
            amount = isValidNumber(amount)
              ? echarts.format.addCommas(amount * 1000) + '$'
              : '-';
            let amount2011 = value[1];
            amount2011 = isValidNumber(amount2011)
              ? echarts.format.addCommas(amount2011 * 1000) + '$'
              : '-';
            let change = value[2];
            change = isValidNumber(change) ? change.toFixed(2) + '%' : '-';
            return [
              '<div class="tooltip-title">' +
                echarts.format.encodeHTML(info.name) +
                '</div>',
              '2012 Amount: &nbsp;&nbsp;' + amount + '<br>',
              '2011 Amount: &nbsp;&nbsp;' + amount2011 + '<br>',
              'Change From 2011: &nbsp;&nbsp;' + change
            ].join('');
          }
        },
        series: [
          {
            name: 'ALL',
            top: 80,
            type: 'treemap',
            label: {
              show: true,
              formatter: '{b}
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

## Key Points
- This is an official ECharts example from `treemap-visual/main.js`
- Template data format: `[{name: string, value?: number, collapsed?: boolean, children?: [...]}]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
