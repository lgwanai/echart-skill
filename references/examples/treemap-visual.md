# 映射为渐变色 / Gradient Mapping

**Category:** `treemap`
**Example dir:** `treemap-visual`

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
       
```

## Key Points
- Generate via: `scripts/build_template.py treemap/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
