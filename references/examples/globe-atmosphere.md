# å¤§æ°å±æ¾ç¤º

**Category:** `globe`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=globe-atmosphere
**Template:** examples/globe-atmosphere.html
**Data Format:** `N/A`

## Official Option Code

```javascript
/*
title: Globe with Atmosphere
category: globe
titleCN: å¤§æ°å±æ¾ç¤º
difficulty: 1
*/
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

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
