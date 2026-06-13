# 矩形树图和旭日图的动画过渡 / Transition between Treemap and Sunburst

**Category:** `treemap`
**Example dir:** `treemap-sunburst-transition`

## Template
- **treemap/basic.html** — Treemap
Data format: `[{name: string, value?: number, children?: [...]}, ...]`

## Option Code
```javascript
$.getJSON(
  ROOT_PATH + '/data/asset/data/echarts-package-size.json',
  function (data) {
    const treemapOption = {
      series: [
        {
          type: 'treemap',
          id: 'echarts-package-size',
          animationDurationUpdate: 1000,
          roam: false,
          nodeClick: undefined,
          data: data.children,
          universalTransition: true,
          label: {
            show: true
          },
          breadcrumb: {
            show: false
          }
        }
      ]
    };
    const sunburstOption = {
      series: [
        {
          type: 'sunburst',
          id: 'echarts-package-size',
          radius: ['20%', '90%'],
          animationDurationUpdate: 1000,
          nodeClick: undefined,
          data: data.children,
          universalTransition: true,
          itemStyle: {
            borderWidth: 1,
            borderColor: 'rgba(255,255,255,.5)'
          },
          label: {
            show: false
          }
        }
      ]
    };
    let currentOption = treemapOption;
    myChart.setOption(currentOption);
    setInterval(function () {
      currentOption =
        currentOption === treemapOption ? sunburstOption : treemapOption;
      myChart.setOption(currentOption);
    }, 3000);
  }
);
```

## Key Points
- Generate via: `scripts/build_template.py treemap/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
