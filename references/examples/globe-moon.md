# æç / Moon

**Category:** `globe`
**Example dir:** `globe-moon`

## Template
- **3d/globe.html** — Globe
Data format: `[[lat, lng, value], ...]`

## Option Code
```javascript
option = {
  globe: {
    baseTexture: ROOT_PATH + '/data-gl/asset/moon-base.jpg',
    heightTexture: ROOT_PATH + '/data-gl/asset/moon-bump.jpg',
    displacementScale: 0.05,
    displacementQuality: 'medium',
    environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
    shading: 'realistic',
    realisticMaterial: {
      roughness: 0.8,
      metalness: 0
    },
    postEffect: {
      enable: true,
      SSAO: {
        enable: true,
        radius: 2,
        intensity: 1,
        quality: 'high'
      }
    },
    temporalSuperSampling: {
      enable: true
    },
    light: {
      ambient: {
        intensity: 0
      },
      main: {
        intensity: 2,
        shadow: true
      },
      ambientCubemap: {
        texture: ROOT_PATH + '/data-gl/asset/pisa.hdr',
        exposure: 0,
        diffuseIntensity: 0.02
      }
    },
    viewControl: {
      autoRotate: false
    }
  },
  series: []
};
```

## Key Points
- Generate via: `scripts/build_template.py 3d/globe.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
