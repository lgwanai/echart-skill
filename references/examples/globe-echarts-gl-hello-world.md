# ECharts GL å¥é¨

**Category:** `globe`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=globe-echarts-gl-hello-world
**Template:** examples/globe-echarts-gl-hello-world.html
**Data Format:** `N/A`

## Official Option Code

```javascript
/*
title: ECharts-GL Hello World
category: globe
titleCN: ECharts GL å¥é¨
difficulty: 0
scripts: 'https://echarts.apache.org/zh/js/vendors/echarts-gl/dist/echarts-gl.min.js'
videoStart: 2000
videoEnd: 6000
*/
option = {
  backgroundColor: '#000',
  globe: {
    baseTexture: ROOT_PATH + '/data-gl/asset/world.topo.bathy.200401.jpg',
    heightTexture: ROOT_PATH + '/data-gl/asset/world.topo.bathy.200401.jpg',
    displacementScale: 0.04,
    shading: 'realistic',
    environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
    realisticMaterial: {
      roughness: 0.9
    },
    postEffect: {
      enable: true
    },
    light: {
      main: {
        intensity: 5,
        shadow: true
      },
      ambientCubemap: {
        texture: ROOT_PATH + '/data-gl/asset/pisa.hdr',
        diffuseIntensity: 0.2
      }
    }
  }
};
```

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
