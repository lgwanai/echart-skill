# å¤§æ°å±æ¾ç¤º / Globe with Atmosphere

**Category:** `globe`
**Example dir:** `globe-atmosphere`

## Template
- **3d/globe.html** — Globe
Data format: `[[lat, lng, value], ...]`

## Option Code
```javascript
option = {
  backgroundColor: '#000',
  globe: {
    baseTexture: ROOT_PATH + '/data-gl/asset/earth.jpg',
    shading: 'lambert',
    environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
    atmosphere: {
      show: true
    },
    light: {
      ambient: {
        intensity: 0.1
      },
      main: {
        intensity: 1.5
      }
    }
  },
  series: []
};
```

## Key Points
- Generate via: `scripts/build_template.py 3d/globe.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
