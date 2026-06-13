# Geo3D with Different Height

**Category:** `geo3D`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=geo3d-with-different-height
**Template:** NONE — use knowledge base
**Data Format:** `N/A`

## Official Option Code

```javascript
/*
title: Geo3D with Different Height
category: geo3D
titleCN: Geo3D with Different Height
*/
$.getJSON(
  ROOT_PATH + '/data-gl/asset/data/world-population.json',
  function (populationData) {
    var max = -Infinity;
    var min = Infinity;
    populationData.forEach(function (item) {
      max = Math.max(Math.log(item.value), max);
      min = Math.min(Math.log(item.value), min);
    });
    var regions = populationData.map(function (item) {
      return {
        name: item.name,
        height: ((Math.log(item.value) - min) / (max - min)) * 3
      };
    });
    myChart.setOption(
      (option = {
        backgroundColor: '#cdcfd5',
        geo3D: {
          map: 'world',
          shading: 'lambert',
          lambertMaterial: {
            detailTexture: ROOT_PATH + '/data-gl/asset/woods.jpg',
            textureTiling: 20
          },
          postEffect: {
            enable: true,
            SSAO: {
              enable: true,
              radius: 3,
              quality: 'high'
            }
          },
          groundPlane: {
            show: true
          },
          light: {
            main: {
              intensity: 1,
              shadow: true,
              shadowQuality: 'high',
              alpha: 30
            },
            ambient: {
              intensity: 0
            },
            ambientCubemap: {
              texture: ROOT_PATH + '/data-gl/asset/canyon.hdr',
              exposure: 2,
              diffuseIntensity: 0.3
            }
          },
          viewControl: {
            distance: 50
          },
          regionHeight: 0.5,
          regions: regions
        }
      })
    );
  }
);
```

## Usage
- Build: `scripts/build_template.py N/A -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
