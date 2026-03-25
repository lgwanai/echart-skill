## 图表类型：地理坐标系上的等值区划图和散点图 (Geo Choropleth and Scatter)

**生成指令**：你现在的任务是生成一个 ECharts 的 `option` 配置。请根据以下骨架代码和数据结构要求，结合用户的实际数据进行填充和修改，生成一份完整的图表配置参数。

### 外部数据结构分析
该图表需要特定的外部数据结构支撑。以下是下载后的数据结构示例，请将用户的真实数据映射为类似结构：

**数据文件 [/data/asset/geo/iceland.geo.json]**:
```json
数据是一个对象 (Object)。包含的顶层字段示例：type, features。数据截取示例：
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -14.6146,
              65.9863
            ],
            [
              -14.663,
              65.9811
            ],
            [
              -14.6941,
              65.9438
            ],
            [
              -15.1014,
              65.922
            ],
            [
              -15.1263,
...
```

### ECharts Option 骨架参考
请基于此结构（已剥离冗长写死的数据）生成配置。不要直接输出此骨架，而是要输出**包含真实数据和完整逻辑**的完整 `option` 对象：

```javascript
function createChart() {
  var icelandRoughLatitude = 65;
  option = {
    geo: {
      map: 'iceland',
      roam: true,
      aspectScale: Math.cos((icelandRoughLatitude * Math.PI) / 180),
      // nameProperty: 'name_en', // If using en name.
      label: {
        show: true,
        color: '#555'
      }
    },
    tooltip: {},
    visualMap: [
      {
        orient: 'horizontal',
        calculable: true,
        right: 0,
        bottom: 0,
        seriesIndex: 0,
        // min/max is specified as series.data value extent.
        min: 0,
        max: 1e5,
        dimension: 2,
        inRange: {
          symbolSize: [5, 30]
        },
        controller: {
          inRange: {
            color: ['#66c2a5']
          }
        }
      },
      {
        orient: 'horizontal',
        calculable: true,
        left: 0,
        bottom: 0,
        seriesIndex: 1,
        // min/max is specified as series.data value extent.
        min: 0,
        max: 1e3,
        dimension: 0,
        inRange: {
          color: ['#deebf7', '#3182bd']
        }
      }
    ],
    series: [
      {
        type: 'scatter',
        coordinateSystem: 'geo',
        geoIndex: 0,
        encode: {
          // `2` is the dimension index of series.data
          tooltip: 2,
          label: 2
        },
        data: [
          [-21.9348415, 64.1334671, 14523],
          [-19.028531, 63.710241, 45126],
          [-17.089925, 65.37887072, 12345],
          [-19.15936, 65.6218101, 56789],
          [-19.849175, 65.7287035, 67890],
          [-23.18326, 65.582939, 89012],
          [-14.9515, 64.475135, 34567],
          [-20.88389, 63.85321, 45678]
        ],
        itemStyle: {
          color: '#66c2a5',
          borderWidth: 1,
          borderColor: '#3c7865'
        }
      },
      {
        // Effectively this is a choropleth map.
        type: 'map',
        // Specify geoIndex to share the geo component with the scatter series above,
        // instead of creating an internal geo coord sys.
        geoIndex: 0,
        map: '',
        data: [
          { name: 'Austurland', value: 423 },
          { name: 'Suðurland', value: 256 },
          { name: 'Norðurland vestra', value: 489 },
          { name: 'Norðurland eystra', value: 51 }
        ]
      }
    ]
  };
  myChart.setOption(option);
}
function fetchGeoJSON() {
  myChart.showLoading();
  $.get(ROOT_PATH + '/data/asset/geo/iceland.geo.json', function (geoJSON) {
    echarts.registerMap('iceland', geoJSON);
    createChart();
    myChart.hideLoading();
  });
}
fetchGeoJSON();
```



### 🗺️ Map Fallback Rule (CRITICAL)
**如果用户需要展示的维度在本地 JS 中没有找到**（例如：细分城市维度、其他未涵盖的国家或地区），则**必须**使用 ECharts 百度地图扩展模式（即 `bmap` 模式，或称“AK 模式”）。
- **做法**：移除 `geo` 配置，改为使用 `bmap: { center: [lng, lat], zoom: 5, roam: true }`，并且所有的 map/scatter 系列必须指定 `coordinateSystem: 'bmap'`。
- **依赖**：此模式需要通过百度地图 AK 来渲染底图。生成时务必确保 `chart_generator.py` 能获取到配置好的 `BAIDU_AK`。
