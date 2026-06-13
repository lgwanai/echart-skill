# 3.7 万亿美元支出构成 / How $3.7 Trillion is Spent

**Category:** `treemap`
**Example dir:** `treemap-obama`
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
    function buildData(mode, originList) {
      let out = [];
      for (let i = 0; i < originList.length; i++) {
        let node = originList[i];
        let newNode = cloneNodeInfo(node);
        if (!newNode) {
          continue;
        }
        out[i] = newNode;
        let value = newNode.value;
        // Calculate amount per household.
        value[3] = value[0] / household_america_2012;
        // if mode === 0 and mode === 2 do nothing
        if (mode === 1) {
          // Set 'Change from 2010' to value[0].
          let tmp = value[1];
          value[1] = value[0];
          value[0] = tmp;
        }
        if (node.children) {
          newNode.children = buildData(mode, node.children);
        }
      }
      return out;
    }
    function cloneNodeInfo(node) {
      if (!node) {
        return;
      }
      const newNode = {};
      newNode.name = node.name;
      newNode.id = node.id;
      newNode.value = (node.value || []).slice();
      return newNode;
    }
    function getLevelOption(mode) {
      return [
        {
          color:
            mode === 2
              ? [
                  '#c23531',
                  '#314656',
                  '#61a0a8',
                  '#dd8668',
                  '#91c7ae',
                  '#6e7074',
                  '#61a0a8',
                  '#bda29a',
                  '#44525d',
                  '#c4ccd3'
                ]
              : undefined,
          colorMappingBy: 'id',
          itemStyle: {
            borderWidth: 3,
            gapWidth: 3
          }
        },
        {
          colorAlpha: mode === 2 ? [0.5, 1] : undefined,
          itemStyle: {
            gapWidth: 1
          }
        }
      ];
    }
    function isValidNumber(num) {
      return num != null && isFinite(num);
    }
    function getTooltipFormatter(mode) {
      let amountIndex = mode === 1 ? 1 : 0;
      let amountIndex2011 = mode === 1 ? 0 : 1;
      return function (info) {
        let value = info.value;
        let amount = value[amountIndex];
        amount = isValidNumber(amount)
          ? echarts.format.addCommas(amount * 1000) + '$'
          : '-';
        let amount2011 = value[amountIndex2011];
        amount2011 = isValidNumber(amount2011)
          ? echarts.format.addCommas(amount2011 * 1000) + '$'
          : '-';
        let perHousehold = value[3];
        perHousehold = isValidNumber(perHousehold)
          ? echarts.format.addCommas(+perHousehold.toFixed(4) * 1000) + '$'
          : '-';
        let change = value[2];
        change = isValidNumber(change) ? change.toFixed(2) + '%' : '-';
        return [
          '<div class="tooltip-title">' +
            echarts.format.encodeHTML(info.name) +
            '</div>',
          '2012 Amount: &nbsp;&nbsp;' + am
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
- This is an official ECharts example from `treemap-obama/main.js`
- Template data format: `[{name: string, value?: number, collapsed?: boolean, children?: [...]}]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
