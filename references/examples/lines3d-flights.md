# Flights / Flights

**Category:** `lines3D`
**Example dir:** `lines3d-flights`
**Difficulty:** 

## Template Match
- **3d/lines3d.html** — Lines3D

## Option Code
```javascript
$.getJSON(ROOT_PATH + '/data-gl/asset/data/flights.json', function (data) {
  var airports = data.airports.map(function (item) {
    return {
      coord: [item[3], item[4]]
    };
  });
  function getAirportCoord(idx) {
    return [data.airports[idx][3], data.airports[idx][4]];
  }
  // Route: [airlineIndex, sourceAirportIndex, destinationAirportIndex]
  var routesGroupByAirline = {};
  data.routes.forEach(function (route) {
    var airline = data.airlines[route[0]];
    var airlineName = airline[0];
    if (!routesGroupByAirline[airlineName]) {
      routesGroupByAirline[airlineName] = [];
    }
    routesGroupByAirline[airlineName].push(route);
  });
  var pointsData = [];
  data.routes.forEach(function (airline) {
    pointsData.push(getAirportCoord(airline[1]));
    pointsData.push(getAirportCoord(airline[2]));
  });
  var series = data.airlines
    .map(function (airline) {
      var airlineName = airline[0];
      var routes = routesGroupByAirline[airlineName];
      if (!routes) {
        return null;
      }
      return {
        type: 'lines3D',
        name: airlineName,
        effect: {
          show: true,
          trailWidth: 2,
          trailLength: 0.15,
          trailOpacity: 1,
          trailColor: 'rgb(30, 30, 60)'
        },
        lineStyle: {
          width: 1,
          color: 'rgb(50, 50, 150)',
          // color: 'rgb(118, 233, 241)',
          opacity: 0.1
        },
        blendMode: 'lighter',
        data: routes.map(function (item) {
          return [airports[item[1]].coord, airports[item[2]].coord];
        })
      };
    })
    .filter(function (series) {
      return !!series;
    });
  series.push({
    type: 'scatter3D',
    coordinateSystem: 'globe',
    blendMode: 'lighter',
    symbolSize: 2,
    itemStyle: {
      color: 'rgb(50, 50, 150)',
      opacity: 0.2
    },
    data: pointsData
  });
  myChart.setOption({
    legend: {
      selectedMode: 'single',
      left: 'left',
      data: Object.keys(routesGroupByAirline),
      orient: 'vertical',
      textStyle: {
        color: '#fff'
      }
    },
    globe: {
      environment: ROOT_PATH + '/data-gl/asset/starfield.jpg',
      heightTexture:
        ROOT_PATH + '/data-gl/asset/bathymetry_bw_composite_4k.jpg',
      displacementScale: 0.1,
      displacementQuality: 'high',
      baseColor: '#000',
      shading: 'realistic',
      realisticMaterial: {
        roughness: 0.2,
        metalness: 0
      },
      postEffect: {
        enable: true,
        depthOfField: {
          enable: false,
          focalDistance: 150
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
          intensity: 0.1,
          shadow: false
        },
        ambientCubemap: {
          texture: ROOT_PATH + '/data-gl/asset/lake.hdr',
          exposure: 1,
          diffuseIntensity: 0.5,
          specularIntensity: 2
        }
      },
      vie
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
- This is an official ECharts example from `lines3d-flights/main.js`
- Template data format: `{ geoCoordMap: {"name": [lng, lat]}, flights: [[fromName, toName], ...] }`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
