# 历代绘画大师的色彩运用

**Category:** `scatter`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-painter-choice
**Template:** scatter/basic.html
**Data Format:** `[[x, y], [x, y], ...]`
**Features:** per-item colors via itemStyle

## Official Option Code

```javascript
/*
title: Master Painter Color Choices Throughout History
category: scatter
titleCN: 历代绘画大师的色彩运用
difficulty: 9
*/
myChart.showLoading();
$.get(
  ROOT_PATH + '/data/asset/data/masterPainterColorChoice.json',
  function (json) {
    myChart.hideLoading();
    var data = json[0].x.map(function (x, idx) {
      return [+x, +json[0].y[idx]];
    });
    myChart.setOption(
      (option = {
        title: {
          text: 'Master Painter Color Choices Throughout History',
          subtext: 'Data From Plot.ly',
          left: 'right'
        },
        xAxis: {
          type: 'value',
          splitLine: {
            show: false
          },
          scale: true,
          splitNumber: 5,
          max: 'dataMax',
          axisLabel: {
            formatter: function (val) {
              return val + 's';
            }
          }
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 360,
          interval: 60,
          name: 'Hue',
          splitLine: {
            show: false
          }
        },
        series: [
          {
            name: 'scatter',
            type: 'scatter',
            symbolSize: function (val, param) {
              return (
                json[0].marker.size[param.dataIndex] / json[0].marker.sizeref
              );
            },
            itemStyle: {
              color: function (param) {
                return json[0].marker.color[param.dataIndex];
              }
            },
            data: data
          }
        ]
      })
    );
  }
);
```

## Usage
- Build: `scripts/build_template.py scatter/basic.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
