# 各国人均寿命与GDP关系演变 / Life Expectancy and GDP

**Category:** `scatter`
**Example dir:** `scatter-life-expectancy-timeline`

## Template
- **scatter/bubble.html** — Bubble Scatter
Data format: `[[x, y, sizeValue], ...]`

## Option Code
```javascript
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/data/life-expectancy.json', function (data) {
  myChart.hideLoading();
  var itemStyle = {
    opacity: 0.8
  };
  var sizeFunction = function (x) {
    var y = Math.sqrt(x / 5e8) + 0.1;
    return y * 80;
  };
  // Schema:
  var schema = [
    { name: 'Income', index: 0, text: '人均收入', unit: '美元' },
    { name: 'LifeExpectancy', index: 1, text: '人均寿命', unit: '岁' },
    { name: 'Population', index: 2, text: '总人口', unit: '' },
    { name: 'Country', index: 3, text: '国家', unit: '' }
  ];
  option = {
    baseOption: {
      timeline: {
        axisType: 'category',
        orient: 'vertical',
        autoPlay: true,
        inverse: true,
        playInterval: 1000,
        left: null,
        right: 0,
        top: 20,
        bottom: 20,
        width: 55,
        height: null,
        symbol: 'none',
        checkpointStyle: {
          borderWidth: 2
        },
        controlStyle: {
          showNextBtn: false,
          showPrevBtn: false
        },
        data: []
      },
      title: [
        {
          text: data.timeline[0],
          textAlign: 'center',
          left: '63%',
          top: '55%',
          textStyle: {
            fontSize: 100
          }
        },
        {
          text: '各国人均寿命与GDP关系演变',
          left: 'center',
          top: 10,
          textStyle: {
            fontWeight: 'normal',
            fontSize: 20
          }
        }
      ],
      tooltip: {
        padding: 5,
        borderWidth: 1,
        formatter: function (obj) {
          var value = obj.value;
          // prettier-ignore
          return schema[3].text + '：' + value[3] + '<br>'
                        + schema[1].text + '：' + value[1] + schema[1].unit + '<br>'
                        + schema[0].text + '：' + value[0] + schema[0].unit + '<br>'
                        + schema[2].text + '：' + value[2] + '<br>';
        }
      },
      grid: {
        top: 100,
        containLabel: true,
        le
```

## Key Points
- Generate via: `scripts/build_template.py scatter/bubble.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
