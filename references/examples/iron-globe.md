# iron-globe

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=iron-globe

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Iron globe
category: globe
titleCN: éè´¨æå°ç
*/
option = {
  backgroundColor: '#000',
  globe: {
    baseTexture: ROOT_PATH + '/data-gl/asset/world.topo.bathy.200401.jpg',
    heightTexture: ROOT_PATH + '/data-gl/asset/bathymetry_bw_composite_4k.jpg',
    displacementScale: 0.2,
    shading: 'realistic',
    environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
    realisticMaterial: {
      roughness: ROOT_PATH + '/asset/get/s/data-1497599804873-H1SHkG-mZ.jpg',
      metalness: ROOT_PATH + '/asset/get/s/data-1497599800643-BJbHyGWQW.jpg',
      textureTiling: [8, 4]
    },
    postEffect: {
      enable: true
    },
    viewControl: {
      autoRotate: false
    },
    light: {
      main: {
        intensity: 2,
        shadow: true
      },
      ambientCubemap: {
        texture: ROOT_PATH + '/data-gl/asset/pisa.hdr',
        exposure: 2,
        diffuseIntensity: 2,
        specularIntensity: 2
      }
    }
  }
};
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
