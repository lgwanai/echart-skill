# globe-atmosphere

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=globe-atmosphere
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
