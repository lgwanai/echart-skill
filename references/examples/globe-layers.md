# å°çå¾å±

**Category:** `globe`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=globe-layers
**Template:** examples/globe-layers.html
**Data Format:** `N/A`

## Official Option Code

```javascript
/*
title: Globe Layers
category: globe
titleCN: å°çå¾å±
difficulty: 1
videoStart: 2000
videoEnd: 6000
*/
option = {
  backgroundColor: '#000',
  globe: {
    baseTexture: ROOT_PATH + '/data-gl/asset/earth.jpg',
    heightTexture: ROOT_PATH + '/data-gl/asset/bathymetry_bw_composite_4k.jpg',
    displacementScale: 0.1,
    shading: 'lambert',
    environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
    light: {
      ambient: {
        intensity: 0.1
      },
      main: {
        intensity: 1.5
      }
    },
    layers: [
      {
        type: 'blend',
        blendTo: 'emission',
        texture: ROOT_PATH + '/data-gl/asset/night.jpg'
      },
      {
        type: 'overlay',
        texture: ROOT_PATH + '/data-gl/asset/clouds.png',
        shading: 'lambert',
        distance: 5
      }
    ]
  },
  series: []
};
```

## Placeholders

| Placeholder | Type | Description |
|-------------|------|-------------|
| `{{{TITLE}}}` | string | title |

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
