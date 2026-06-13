# Flights GL / Flights GL

**Category:** `lines3D`
**Example dir:** `lines3d-flights-gl`
**Difficulty:** 

## Template Match
- **3d/lines3d.html** — Lines3D

## Option Code
```javascript
var uploadedDataURL = ROOT_PATH + '/data-gl/asset/data/flights.json';
myChart.showLoading();
$.getJSON(uploadedDataURL, function (data) {
  myChart.hideLoading();
  function getAirportCoord(idx) {
    return [data.airports[idx][3], data.airports[idx][4]];
  }
  var routes = data.routes.map(function (airline) {
    return [getAirportCoord(airline[1]), getAirportCoord(airline[2])];
  });
  myChart.setOption({
    geo3D: {
      map: 'world',
      shading: 'realistic',
      silent: true,
      environment: '#333',
      realisticMaterial: {
        roughness: 0.8,
        metalness: 0
      },
      postEffect: {
        enable: true
      },
      groundPlane: {
        show: false
      },
      light: {
        main: {
          intensity: 1,
          alpha: 30
        },
        ambient: {
          intensity: 0
        }
      },
      viewControl: {
        distance: 70,
        alpha: 89,
        panMouseButton: 'left',
        rotateMouseButton: 'right'
      },
      itemStyle: {
        color: '#000'
      },
      regionHeight: 0.5
    },
    series: [
      {
        type: 'lines3D',
        coordinateSystem: 'geo3D',
        effect: {
          show: true,
          trailWidth: 1,
          trailOpacity: 0.5,
          trailLength: 0.2,
          constantSpeed: 5
        },
        blendMode: 'lighter',
        lineStyle: {
          width: 0.2,
          opacity: 0.05
        },
        data: routes
      }
    ]
  });
  window.addEventListener('keydown', function () {
    myChart.dispatchAction({
      type: 'lines3DToggleEffect',
      seriesIndex: 0
    });
  });
});
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

## #31
 — Lines3D 空白：GEO_COORD_MAP 为空 + BASE_TEXTURE 缺失
- **日期**：2026-06-13
- **现象**：37_3D_Lines3D 一片空白
- **根因**：(1) `GEO_COORD_MAP: "{}"` 空对象，FLIGHTS 使用不存在的地名 "A/B/C"；(2) `BASE_TEXTURE: ""` 无地球纹理；(3) GL_INLINE 破坏注入（同 #18）
- **修复**：(1) GEO_COORD_MAP 提供真实城市经纬度；(2) FLIGHTS 改用真实城市名 `[["北京","上海"],...]`；(3) BASE_TEXTURE 使用真实地球纹理；(4) **模板守卫**：`geoCoordMap || {}`

---
...

## Key Points
- This is an official ECharts example from `lines3d-flights-gl/main.js`
- Template data format: `{ geoCoordMap: {"name": [lng, lat]}, flights: [[fromName, toName], ...] }`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
