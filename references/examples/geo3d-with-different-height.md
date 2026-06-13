# Geo3D with Different Height / Geo3D with Different Height

**Category:** `geo3D`
**Example dir:** `geo3d-with-different-height`
**Difficulty:** 

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
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



## Key Points
- This is an official ECharts example from `geo3d-with-different-height/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
