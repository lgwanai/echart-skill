# geo-organ

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=geo-organ
**Chart Type:** `bar`

## User Data Requirements

Columns needed: need **category** + **value** columns

## Data Arrays — Replacement Guide

The code contains **2 data array(s)** to replace:

### data[0]: `yAxis`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [
          'heart',
          'large-intestine',
          'small-intestine',
          'sple...`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `series[0]`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: [121, 321, 141, 52, 198, 289, 139]`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Organ Data with SVG
category: map
titleCN: 内脏数据（SVG）
*/
$.get(
  ROOT_PATH + '/data/asset/geo/Veins_Medical_Diagram_clip_art.svg',
  function (svg) {
    echarts.registerMap('organ_diagram', { svg: svg });
    option = {
      tooltip: {},
      geo: {
        left: 10,
        right: '50%',
        map: 'organ_diagram',
        selectedMode: 'multiple',
        emphasis: {
          focus: 'self',
          itemStyle: {
            color: null
          },
          label: {
            position: 'bottom',
            distance: 0,
            textBorderColor: '#fff',
            textBorderWidth: 2
          }
        },
        blur: {},
        select: {
          itemStyle: {
            color: '#b50205'
          },
          label: {
            show: false,
            textBorderColor: '#fff',
            textBorderWidth: 2
          }
        }
      },
      grid: {
        left: '60%',
        top: '20%',
        bottom: '20%'
      },
      xAxis: {},
      yAxis: {
        data: [
          'heart',
          'large-intestine',
          'small-intestine',
          'spleen',
          'kidney',
          'lung',
          'liver'
        ]
      },
      series: [
        {
          type: 'bar',
          emphasis: {
            focus: 'self'
          },
          data: [121, 321, 141, 52, 198, 289, 139]
        }
      ]
    };
    myChart.setOption(option);
    myChart.on('mouseover', { seriesIndex: 0 }, function (event) {
      myChart.dispatchAction({
        type: 'highlight',
        geoIndex: 0,
        name: event.name
      });
    });
    myChart.on('mouseout', { seriesIndex: 0 }, function (event) {
      myChart.dispatchAction({
        type: 'downplay',
        geoIndex: 0,
        name: event.name
      });
    });
  }
);
```
