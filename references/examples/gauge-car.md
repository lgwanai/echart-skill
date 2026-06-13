# 汽车仪表盘 / Gauge Car

**Category:** `gauge`
**Example dir:** `gauge-car`
**Difficulty:** 8

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
option = {
  backgroundColor: '#000',
  tooltip: {
    formatter: '{a} <br/>{b} : {c}%'
  },
  toolbox: {
    feature: {
      restore: {},
      saveAsImage: {}
    }
  },
  series: [
    // left
    {
      name: 'gauge 0',
      type: 'gauge',
      min: -200,
      max: 250,
      startAngle: -30,
      endAngle: -315,
      splitNumber: 9,
      radius: '35%',
      center: ['21%', '55%'],
      axisLine: {
        lineStyle: {
          color: [[1, '#AE96A6']]
        }
      },
      splitLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        show: false
      },
      anchor: {},
      pointer: {
        show: false
      },
      detail: {
        show: false
      },
      title: {
        fontSize: 12,
        fontWeight: 800,
        fontFamily: 'Arial',
        color: '#fff',
        offsetCenter: [0, '-60%']
      },
      progress: {
        show: true,
        width: 3,
        itemStyle: {
          color: '#fff'
        }
      },
      data: [
        {
          value: 250,
          name: 'km/h'
        }
      ]
    },
    {
      name: 'gauge 1',
      type: 'gauge',
      min: 0,
      max: 250,
      startAngle: -140,
      endAngle: -305,
      splitNumber: 5,
      radius: '35%',
      center: ['21%', '55%'],
      axisLine: {
        lineStyle: {
          color: [[1, '#AE96A6']]
        }
      },
      splitLine: {
        distance: -7,
        length: 12,
        lineStyle: {
          color: '#fff',
          width: 4
        }
      },
      axisTick: {
        distance: -8,
        length: 8,
        lineStyle: {
          color: '#fff',
          width: 2
        }
      },
      axisLabel: {
        distance: 14,
        fontSize: 18,
        fontWeight: 800,
        fontFamily: 'Arial',
        color: '#fff'
      },
      anchor: {},
      pointer: {
        icon: 'path://M-36.5,23.9L-41,4.4c-0.1-0.4-0.4-0.7-0.7-0.7c-0.5-0.1-1.1,0.2-1.2,0.7l-4.5,19.5c0,0.1,0,0.1,0,0.2v92.3c0,0.6,0.4,1,1,1h9c0.6,0,1-0.4,1-1V24.1C-36.5,24-36.5,23.9-36.5,23.9z M-39.5,114.6h-5v-85h5V114.6z',
        width: 5,
        length: '40%',
        offsetCenter: [0, '-58%'],
        itemStyle: {
          color: '#f00',
          shadowColor: 'rgba(255, 0, 0)',
          shadowBlur: 5,
          shadowOffsetY: 2
        }
      },
      title: {
        color: '#fff',
        fontSize: 14,
        fontWeight: 800,
        fontFamily: 'Arial',
        offsetCenter: [0, 0]
      },
      detail: {
        show: false
      },
      data: [
        {
          value: 0,
          name: '当前位置：\n \n 中科路'
        }
      ]
    },
    // middle
    {
      name: 'gauge 2',
      type: 'gauge',
      min: 0,
      max: 8,
      z: 10,
      startAngle: 210,
      endAngle: -30,
      splitNumber: 8,
      radius: '50%',
      center: ['50%', '50%'],
      axisLine: {
        show: true,
        lineStyle: {
          width: 0,
          color: [
            [0.825, '#fff'],
            [1, '
```



## Key Points
- This is an official ECharts example from `gauge-car/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
