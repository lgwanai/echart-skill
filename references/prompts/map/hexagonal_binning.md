## 图表类型：六边形分箱图（自定义系列） (Hexagonal Binning)

**生成指令**：你现在的任务是生成一个 ECharts 的 `option` 配置。请根据以下骨架代码和数据结构要求，结合用户的实际数据进行填充和修改，生成一份完整的图表配置参数。

### 外部数据结构分析
该图表需要特定的外部数据结构支撑。以下是下载后的数据结构示例，请将用户的真实数据映射为类似结构：

**数据文件 [/data/asset/data/kawhi-leonard-16-17-regular.json]**:
```json
数据是一个对象 (Object)。包含的顶层字段示例：schema, data。数据截取示例：
{
  "schema": [
    "grid_type",
    "game_id",
    "game_event_id",
    "player_id",
    "player_name",
    "team_id",
    "team_name",
    "period",
    "minutes_remaining",
    "seconds_remaining",
    "event_type",
    "action_type",
    "shot_type",
    "shot_zone_basic",
    "shot_zone_area",
    "shot_zone_range",
    "shot_distance",
    "loc_x",
    "loc_y",
    "shot_attempted_flag",
    "shot_made_flag",
    "game_date",
    "htm",
    "vtm",
    "shot_made_numeric",
    "shot_value"
...
```

**数据文件 [/data/asset/data/nba-court.json]**:
```json
数据是一个对象 (Object)。包含的顶层字段示例：borderGeoJSON, hexbinExtent, width, height, geometry。数据截取示例：
{
  "borderGeoJSON": {
    "type": "FeatureCollection",
    "features": [
      {
        "geometry": {
          "type": "Polygon",
          "coordinates": [
            [
              [
                -27,
                -2
              ],
              [
                -27,
                49
              ],
              [
                27,
                49
              ],
              [
                27,
                -2
              ]
            ]
          ]
        },
...
```

### ECharts Option 骨架参考
请基于此结构（已剥离冗长写死的数据）生成配置。不要直接输出此骨架，而是要输出**包含真实数据和完整逻辑**的完整 `option` 对象：

```javascript
// Hexbin statistics code based on [d3-hexbin](https://github.com/d3/d3-hexbin)
function hexBinStatistics(points, r) {
  var dx = r * 2 * Math.sin(Math.PI / 3);
  var dy = r * 1.5;
  var binsById = {};
  var bins = [];
  for (var i = 0, n = points.length; i < n; ++i) {
    var point = points[i];
    var px = point[0];
    var py = point[1];
    if (isNaN(px) || isNaN(py)) {
      continue;
    }
    var pj = Math.round((py = py / dy));
    var pi = Math.round((px = px / dx - (pj & 1) / 2));
    var py1 = py - pj;
    if (Math.abs(py1) * 3 > 1) {
      var px1 = px - pi;
      var pi2 = pi + (px < pi ? -1 : 1) / 2;
      var pj2 = pj + (py < pj ? -1 : 1);
      var px2 = px - pi2;
      var py2 = py - pj2;
      if (px1 * px1 + py1 * py1 > px2 * px2 + py2 * py2) {
        pi = pi2 + (pj & 1 ? 1 : -1) / 2;
        pj = pj2;
      }
    }
    var id = pi + '-' + pj;
    var bin = binsById[id];
    if (bin) {
      bin.points.push(point);
    } else {
      bins.push((bin = binsById[id] = { points: [point] }));
      bin.x = (pi + (pj & 1) / 2) * dx;
      bin.y = pj * dy;
    }
  }
  var maxBinLen = -Infinity;
  for (var i = 0; i < bins.length; i++) {
    maxBinLen = Math.max(maxBinLen, bins.length);
  }
  return {
    maxBinLen: maxBinLen,
    bins: bins
  };
}
$.when(
  $.getJSON(ROOT_PATH + '/data/asset/data/kawhi-leonard-16-17-regular.json'),
  $.getJSON(ROOT_PATH + '/data/asset/data/nba-court.json')
).done(function (shotData, nbaCourt) {
  shotData = shotData[0];
  nbaCourt = nbaCourt[0];
  echarts.registerMap('nbaCourt', nbaCourt.borderGeoJSON);
  var backgroundColor = '#333';
  var hexagonRadiusInGeo = 1;
  var hexBinResult = hexBinStatistics(
    shotData.data.map(function (item) {
      // "shot_made_flag" made missed
      var made = item[shotData.schema.indexOf('shot_made_flag')];
      return [
        item[shotData.schema.indexOf('loc_x')],
        item[shotData.schema.indexOf('loc_y')],
        made === 'made' ? 1 : 0
      ];
    }),
    hexagonRadiusInGeo
  );
  var data = hexBinResult.bins.map(function (bin) {
    var made = 0;
    bin.points.forEach(function (point) {
      made += point[2];
    });
    return [
      bin.x,
      bin.y,
      bin.points.length,
      ((made / bin.points.length) * 100).toFixed(2)
    ];
  });
  function renderItemHexBin(params, api) {
    var center = api.coord([api.value(0), api.value(1)]);
    var points = [];
    var pointsBG = [];
    var maxViewRadius = api.size([hexagonRadiusInGeo, 0])[0];
    var minViewRadius = Math.min(maxViewRadius, 4);
    var extentMax = Math.log(Math.sqrt(hexBinResult.maxBinLen));
    var viewRadius = echarts.number.linearMap(
      Math.log(Math.sqrt(api.value(2))),
      [0, extentMax],
      [minViewRadius, maxViewRadius]
    );
    var angle = Math.PI / 6;
    for (var i = 0; i < 6; i++, angle += Math.PI / 3) {
      points.push([
        center[0] + viewRadius * Math.cos(angle),
        center[1] + viewRadius * Math.sin(angle)
      ]);
      pointsBG.push([
        center[0] + maxViewRadius * Math.cos(angle),
        center[1] + maxViewRadius * Math.sin(angle)
      ]);
    }
    return {
      type: 'group',
      children: [
        {
          type: 'polygon',
          shape: {
            points: points
          },
          style: {
            stroke: '#ccc',
            fill: api.visual('color'),
            lineWidth: 1
          }
        },
        {
          type: 'polygon',
          shape: {
            points: pointsBG
          },
          style: {
            stroke: null,
            fill: 'rgba(0,0,0,0.5)',
            lineWidth: 0
          },
          z2: -19
        }
      ]
    };
  }
  function renderItemNBACourt(param, api) {
    return {
      type: 'group',
      children: nbaCourt.geometry.map(function (item) {
        return {
          type: item.type,
          style: {
            stroke: '#aaa',
            fill: null,
            lineWidth: 1.5
          },
          shape: {
            points: item.points.map(api.coord)
          }
        };
      })
    };
  }
  option = {
    backgroundColor: backgroundColor,
    tooltip: {
      backgroundColor: 'rgba(255,255,255,0.9)',
      textStyle: {
        color: '#333'
      }
    },
    animation: false,
    title: {
      text: 'Some Player',
      subtext: 'Regular Season',
      backgroundColor: backgroundColor,
      top: 10,
      left: 10,
      textStyle: {
        color: '#eee'
      }
    },
    legend: {
      data: ['bar', 'error']
    },
    geo: {
      left: 0,
      right: 0,
      top: 0,
      bottom: 0,
      roam: true,
      silent: true,
      itemStyle: {
        color: backgroundColor,
        borderWidth: 0
      },
      map: 'nbaCourt'
    },
    visualMap: {
      type: 'continuous',
      orient: 'horizontal',
      right: 30,
      top: 40,
      min: 0,
      max: 100,
      align: 'bottom',
      text: [null, 'FG:   '],
      dimension: 3,
      calculable: true,
      textStyle: {
        color: '#eee'
      },
      formatter: '{value} %',
      inRange: {
        // color: ['rgba(241,222,158, 0.3)', 'rgba(241,222,158, 1)']
        color: ['green', 'yellow']
      }
    },
    series: [
      {
        type: 'custom',
        coordinateSystem: 'geo',
        geoIndex: 0,
        renderItem: renderItemHexBin,
        dimensions: [
          null,
          null,
          'Field Goals Attempted (hexagon size)',
          'Field Goal Percentage (color)'
        ],
        encode: {
          tooltip: [2, 3]
        },
        data: data
      },
      {
        coordinateSystem: 'geo',
        type: 'custom',
        geoIndex: 0,
        renderItem: renderItemNBACourt,
        silent: true,
        data: [0]
      }
    ]
  };
  myChart.setOption(option);
});
```



### 🗺️ Map Fallback Rule (CRITICAL)
**如果用户需要展示的维度在本地 JS 中没有找到**（例如：细分城市维度、其他未涵盖的国家或地区），则**必须**使用 ECharts 百度地图扩展模式（即 `bmap` 模式，或称“AK 模式”）。
- **做法**：移除 `geo` 配置，改为使用 `bmap: { center: [lng, lat], zoom: 5, roam: true }`，并且所有的 map/scatter 系列必须指定 `coordinateSystem: 'bmap'`。
- **依赖**：此模式需要通过百度地图 AK 来渲染底图。生成时务必确保 `chart_generator.py` 能获取到配置好的 `BAIDU_AK`。
