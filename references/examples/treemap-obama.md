# 3.7 万亿美元支出构成 / How $3.7 Trillion is Spent

**Category:** `treemap`
**Example dir:** `treemap-obama`

## Template
- **treemap/basic.html** — Treemap
Data format: `[{name: string, value?: number, children?: [...]}, ...]`

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
      return num != null && isFin
```

## Key Points
- Generate via: `scripts/build_template.py treemap/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
