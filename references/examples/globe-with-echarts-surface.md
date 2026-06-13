# Globe with ECharts Surface / Globe with ECharts Surface

**Category:** `globe`
**Example dir:** `globe-with-echarts-surface`

## Template
- **3d/globe.html** — Globe
Data format: `[[lat, lng, value], ...]`

## Option Code
```javascript
var canvas = document.createElement('canvas');
var mapChart = echarts.init(canvas, null, {
  width: 4096,
  height: 2048
});
mapChart.setOption({
  backgroundColor: '#fff',
  visualMap: {
    show: false,
    min: 0,
    max: 500000,
    inRange: {
      color: [
        '#313695',
        '#4575b4',
        '#74add1',
        '#abd9e9',
        '#e0f3f8',
        '#ffffbf',
        '#fee090',
        '#fdae61',
        '#f46d43',
        '#d73027',
        '#a50026'
      ]
    }
  },
  series: [
    {
      type: 'map',
      map: 'world',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      boundingCoords: [
        [-180, 90],
        [180, -90]
      ],
      data: [
        { name: 'Afghanistan', value: 28397.812 },
        { name: 'Angola', value: 19549.124 },
        { name: 'Albania', value: 3150.143 },
        { name: 'United Arab Emirates', value: 8441.537 },
        { name: 'Argentina', value: 40374.224 },
        { name: 'Armenia', value: 2963.496 },
        { name: 'French Southern and Antarctic Lands', value: 268.065 },
        { name: 'Australia', value: 22404.488 },
        { name: 'Austria', value: 8401.924 },
        { name: 'Azerbaijan', value: 9094.718 },
        { name: 'Burundi', value: 9232.753 },
        { name: 'Belgium', value: 10941.288 },
        { name: 'Benin', value: 9509.798 },
        { name: 'Burkina Faso', value: 15540.284 },
        { name: 'Bangladesh', value: 151125.475 },
        { name: 'Bulgaria', value: 7389.175 },
        { name: 'The Bahamas', value: 66402.316 },
        { name: 'Bosnia and Herzegovina', value: 3845.929 },
        { name: 'Belarus', value: 9491.07 },
        { name: 'Belize', value: 308.595 },
        { name: 'Bermuda', value: 64.951 },
        { name: 'Bolivia', value: 716.939 },
        { name: 'Brazil', value: 195210.154 },
        { name: 'Brunei', value: 27.223 },
        { name: 'Bhutan', value: 716.939 },
        { name: 'Botswana', value: 1969.341 },
        { name: 'Central African
```

## Key Points
- Generate via: `scripts/build_template.py 3d/globe.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
