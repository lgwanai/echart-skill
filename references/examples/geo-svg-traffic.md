# 交通（SVG） / GEO SVG Traffic

**Category:** `map`
**Example dir:** `geo-svg-traffic`

## Template
- **geo/lines.html** — 
Data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`

## Option Code
```javascript
$.get(ROOT_PATH + '/data/asset/geo/ksia-ext-plan-min.svg', function (svg) {
  echarts.registerMap('ksia-ext-plan', { svg: svg });
  option = {
    tooltip: {},
    geo: {
      map: 'ksia-ext-plan',
      roam: true,
      layoutCenter: ['50%', '50%'],
      layoutSize: '100%'
    },
    series: [
      {
        name: 'Route',
        type: 'lines',
        coordinateSystem: 'geo',
        geoIndex: 0,
        emphasis: {
          label: {
            show: false
          }
        },
        polyline: true,
        lineStyle: {
          color: '#c46e54',
          width: 0
        },
        effect: {
          show: true,
          period: 8,
          color: '#a10000',
          // constantSpeed: 80,
          trailLength: 0,
          symbolSize: [12, 30],
          symbol:
            'path://M87.1667 3.8333L80.5.5h-60l-6.6667 3.3333L.5 70.5v130l10 10h80l10 -10v-130zM15.5 190.5l15 -20h40l15 20zm75 -65l-15 5v35l15 15zm-80 0l15 5v35l-15 15zm65 0l15 -5v-40l-15 20zm-50 0l-15 -5v-40l15 20zm 65,-55 -15,25 c -15,-5 -35,-5 -50,0 l -15,-25 c 25,-15 55,-15 80,0 z'
        },
        z: 100,
        data: [
          {
            effect: {
              color: '#a10000',
              constantSpeed: 100,
              delay: 0
            },
            coords: [
              [50.875133928571415, 242.66287667410717],
              [62.03696428571425, 264.482421875],
              [72.63357421874997, 273.62779017857144],
              [92.78291852678569, 285.869140625],
              [113.43637834821425, 287.21854073660717],
              [141.44788783482142, 288.92947823660717],
              [191.71686104910714, 289.5507114955357],
              [198.3060072544643, 294.0673828125],
              [204.99699497767858, 304.60288783482144],
              [210.79177734375003, 316.7373046875],
              [212.45179408482142, 329.3656529017857],
              [210.8885267857143, 443.3925083705358],
              [215.35936941964286, 453.00634765625],
              [224
```

## Key Points
- Generate via: `scripts/build_template.py geo/lines.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
