# å°å½¢ä½ç§» / Globe Displacement

**Category:** `globe`
**Example dir:** `globe-displacement`
**Difficulty:** 

## Template Match
- **3d/globe.html** — Globe

## Option Code
```javascript
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
- This is an official ECharts example from `globe-displacement/main.js`
- Template data format: `[[lat, lng, value], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
