# Country Carousel / Country Carousel

**Category:** `globe`
**Example dir:** `globe-country-carousel`
**Difficulty:** 

## Template Match
- **3d/globe.html** — Globe

## Option Code
```javascript
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

## Relevant Debug Patterns
## #28
 — 3D Scatter/Surface/Globe/Lines3D 同样空白
- **日期**：2026-06-13
- **现象**：34/35/36/37 全部空白
- **根因**：与 #27 相同——GL_INLINE 破坏注入 + 模板配置偏离官方示例。所有 3D 模板统一修复
- **修复**：3d/scatter3d.html、3d/surface.html、3d/globe.html、3d/lines3d.html 全部改为与官方示例一致的配置。关键：`zAxis3D: {}`（非 `{type:'value'}`）、`grid3D: {}`、无 `coordinateSystem`

---
...

## #30
 — Globe 无纹理显示为纯色/空白球
- **日期**：2026-06-13
- **现象**：36_3D_Globe 显示为纯蓝/黄色球，无地球纹理
- **根因**：未提供 `baseTexture`，ECharts globe 渲染为无纹理球体
- **修复**：下载 ECharts 官方示例的 1.3MB JPG 地球纹理（`echarts.apache.org/examples/data-gl/asset/world.topo.bathy.200401.jpg`），base64 嵌入为 `baseTexture`

---
...

## Key Points
- This is an official ECharts example from `globe-country-carousel/main.js`
- Template data format: `[[lat, lng, value], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
