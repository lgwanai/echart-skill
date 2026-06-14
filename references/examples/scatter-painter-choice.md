# scatter-painter-choice

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-painter-choice
**Chart Type:** `value`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:


## External Data Format

This example uses external data. Format from `masterPainterColorChoice.json`:

```json
[
  {
    "uid": "12a671",
    "text": [
      "Perikopenbuch Heinrichs II., Szene by Unknown.",
      "Aufklrung nach dem Schneefall am Flu by NA",
      " by Cui Bai",
      " by Guo Xi",
      "Herbst im Flutal by Guo Xi",
      "Predigtsammlungen des Mnchs Johannes von Kokkinobaphos ber die Jungfrau Maria, Szene by Unknown.",
      "Predigtsammlungen des Mnchs Johannes von Kokkinobaphos ber die Jungfrau Maria, Szene by Unknown.",
      "Koran, Szene by Unknown.",
      "Kitb ad-Diryq (Buch d
...
```

Agent: build DuckDB query to produce matching data structure.
## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

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
