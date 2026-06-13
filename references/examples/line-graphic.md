# 自定义图形组件 / Custom Graphic Component

**Category:** `line, graphic`
**Example dir:** `line-graphic`

## Template
- **line/basic.html** — Line
Data format: `{ categories: string[], values: number[] }`

## Option Code
```javascript
option = {
  legend: {
    data: ['Altitude (km) vs Temperature (°C)']
  },
  tooltip: {
    trigger: 'axis',
    formatter: 'Temperature : <br/>{b}km : {c}°C'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    axisLabel: {
      formatter: '{value} °C'
    }
  },
  yAxis: {
    type: 'category',
    axisLine: { onZero: false },
    axisLabel: {
      formatter: '{value} km'
    },
    boundaryGap: true,
    data: ['0', '10', '20', '30', '40', '50', '60', '70', '80']
  },
  graphic: [
    {
      type: 'group',
      rotation: Math.PI / 4,
      bounding: 'raw',
      right: 110,
      bottom: 110,
      z: 100,
      children: [
        {
          type: 'rect',
          left: 'center',
          top: 'center',
          z: 100,
          shape: {
            width: 400,
            height: 50
          },
          style: {
            fill: 'rgba(0,0,0,0.3)'
          }
        },
        {
          type: 'text',
          left: 'center',
          top: 'center',
          z: 100,
          style: {
            fill: '#fff',
            text: 'ECHARTS LINE CHART',
            font: 'bold 26px sans-serif'
          }
        }
      ]
    },
    {
      type: 'group',
      left: '10%',
      top: 'center',
      children: [
        {
          type: 'rect',
          z: 100,
          left: 'center',
          top: 'middle',
          shape: {
            width: 240,
            height: 90
          },
          style: {
            fill: '#fff',
            stroke: '#555',
            lineWidth: 1,
            shadowBlur: 8,
            shadowOffsetX: 3,
            shadowOffsetY: 3,
            shadowColor: 'rgba(0,0,0,0.2)'
          }
        },
        {
          type: 'text',
          z: 100,
          left: 'center',
          top: 'middle',
          style: {
            fill: '#333',
            width: 220,
            overflow: 'break',
            text: 'xAxis represents t
```

## Key Points
- Generate via: `scripts/build_template.py line/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
