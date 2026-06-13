# æç

**Category:** `globe`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=globe-moon
**Template:** NONE — use knowledge base
**Data Format:** `N/A`

## Official Option Code

```javascript
/*
title: Moon
category: globe
titleCN: æç
*/
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

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
