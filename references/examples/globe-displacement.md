# globe-displacement

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=globe-displacement
**Chart Type:** `unknown`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

## Reference Code

```javascript
/*
title: Globe Displacement
category: globe
titleCN: å°å½¢ä½ç§»
*/
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
