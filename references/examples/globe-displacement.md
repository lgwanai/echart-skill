# å°å½¢ä½ç§» / Globe Displacement

**Category:** `globe`
**Example dir:** `globe-displacement`

## Template
- **3d/globe.html** — Globe
Data format: `[[lat, lng, value], ...]`

## Option Code
```javascript
option = {
  globe: {
    displacementTexture:
      ROOT_PATH + '/data-gl/asset/bathymetry_bw_composite_4k.jpg',
    displacementScale: 0.1,
    displacementQuality: 'ultra',
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
        intensity: 1.5,
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
        intensity: 1,
        shadow: true
      },
      ambientCubemap: {
        texture: ROOT_PATH + '/data-gl/asset/pisa.hdr',
        exposure: 1,
        diffuseIntensity: 0.2
      }
    },
    viewControl: {
      autoRotate: false
    },
    debug: {
      wireframe: {
        show: true
      }
    }
  },
  series: []
};
```

## Key Points
- Generate via: `scripts/build_template.py 3d/globe.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
