# 矩形树图和旭日图的动画过渡

**Category:** `treemap`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=treemap-sunburst-transition
**Template:** treemap/basic.html
**Data Format:** `[{name: string, value?: number, children?: [...]}, ...]`
**Features:** labels displayed

## Official Option Code

```javascript
/*
title: Transition between Treemap and Sunburst
category: treemap
titleCN: 矩形树图和旭日图的动画过渡
difficulty: 4
videoStart: 3000
videoEnd: 9000
*/
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

## Usage
- Build: `scripts/build_template.py treemap/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
