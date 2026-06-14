# gauge-temperature

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=gauge-temperature
**Chart Type:** `gauge`

## User Data Requirements

Columns needed: need a single **value** (aggregate)

## Data Arrays — Replacement Guide

The code contains **4 data array(s)** to replace:

### data[0]: `unknown`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
        {
          value: 20
        }
      ]`
- **Replace with**: real data from DuckDB in the same format

### data[1]: `unknown`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
        {
          value: 20
        }
      ]`
- **Replace with**: real data from DuckDB in the same format

### data[2]: `series[0]`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
          {
            value: random
          }
        ]`
- **Replace with**: real data from DuckDB in the same format

### data[3]: `series[0]`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
          {
            value: random
          }
        ]`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Temperature Gauge chart
titleCN: 气温仪表盘
category: gauge
difficulty: 4
videoStart: 2000
videoEnd: 5000
*/
option = {
  series: [
    {
      type: 'gauge',
      center: ['50%', '60%'],
      startAngle: 200,
      endAngle: -20,
      min: 0,
      max: 60,
      splitNumber: 12,
      itemStyle: {
        color: '#FFAB91'
      },
      progress: {
        show: true,
        width: 30
      },
      pointer: {
        show: false
      },
      axisLine: {
        lineStyle: {
          width: 30
        }
      },
      axisTick: {
        distance: -45,
        splitNumber: 5,
        lineStyle: {
          width: 2,
          color: '#999'
        }
      },
      splitLine: {
        distance: -52,
        length: 14,
        lineStyle: {
          width: 3,
          color: '#999'
        }
      },
      axisLabel: {
        distance: -20,
        color: '#999',
        fontSize: 20
      },
      anchor: {
        show: false
      },
      title: {
        show: false
      },
      detail: {
        valueAnimation: true,
        width: '60%',
        lineHeight: 40,
        borderRadius: 8,
        offsetCenter: [0, '-15%'],
        fontSize: 60,
        fontWeight: 'bolder',
        formatter: '{value} °C',
        color: 'inherit'
      },
      data: [
        {
          value: 20
        }
      ]
    },
    {
      type: 'gauge',
      center: ['50%', '60%'],
      startAngle: 200,
      endAngle: -20,
      min: 0,
      max: 60,
      itemStyle: {
        color: '#FD7347'
      },
      progress: {
        show: true,
        width: 8
      },
      pointer: {
        show: false
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        show: false
      },
      axisLabel: {
        show: false
      },
      detail: {
        show: false
      },
      data: [
        {
          value: 20
        }
      ]
    }
  ]
};
setInterval(function () {
  const random = +(Math.random() * 60).toFixed(2);
  myChart.setOption({
    series: [
      {
        data: [
          {
            value: random
          }
        ]
      },
      {
        data: [
          {
            value: random
          }
        ]
      }
    ]
  });
}, 2000);
```
