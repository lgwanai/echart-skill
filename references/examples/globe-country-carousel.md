# globe-country-carousel

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=globe-country-carousel
**Chart Type:** `map`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: need **region name** + **value** columns
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

## Reference Code

```javascript
/*
title: Country Carousel
category: globe
titleCN: Country Carousel
*/
var canvas = document.createElement('canvas');
var mapChart = echarts.init(canvas, null, {
  width: 2048,
  height: 1024
});
mapChart.setOption({
  backgroundColor: '#999',
  geo: {
    type: 'map',
    map: 'world',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    boundingCoords: [
      [-180, 90],
      [180, -90]
    ],
    silent: true,
    itemStyle: {
      borderColor: '#000'
    },
    label: {
      color: '#fff',
      fontSize: 40
    }
  }
});
option = {
  globe: {
    baseTexture: mapChart,
    heightTexture: ROOT_PATH + '/data-gl/asset/bathymetry_bw_composite_4k.jpg',
    displacementScale: 0.1,
    shading: 'realistic',
    realisticMaterial: {
      roughness: 0.8,
      metalness: 0
    },
    postEffect: {
      enable: true
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
        texture: ROOT_PATH + '/data-gl/asset/lake.hdr',
        exposure: 1,
        diffuseIntensity: 0.2
      }
    },
    viewControl: {
      animationDurationUpdate: 1000,
      animationEasingUpdate: 'cubicInOut',
      targetCoord: [116.46, 39.92],
      autoRotate: false
    }
  },
  series: []
};
var regions = mapChart.getModel().getComponent('geo').coordinateSystem.regions;
setInterval(function () {
  var region = regions[Math.round(Math.random() * (regions.length - 1))];
  myChart.setOption({
    title: {
      left: 'center',
      top: 'center',
      text: region.name,
      textStyle: {
        fontSize: 40
      }
    },
    globe: {
      viewControl: {
        targetCoord: region.center
      }
    }
  });
  mapChart.setOption({
    geo: {
      regions: [
        {
          name: region.name,
          itemStyle: {
            normal: {
              areaColor: '#444'
            }
          }
        }
      ]
    }
  });
}, 2000);
```
