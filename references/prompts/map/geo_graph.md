## 图表类型：地理坐标系上的关系图 (Geo Graph)

**生成指令**：你现在的任务是生成一个 ECharts 的 `option` 配置。请根据以下骨架代码和数据结构要求，结合用户的实际数据进行填充和修改，生成一份完整的图表配置参数。

### 外部数据结构分析
该图表需要特定的外部数据结构支撑。以下是下载后的数据结构示例，请将用户的真实数据映射为类似结构：

**数据文件 [/data/asset/geo/ch.geo.json]**:
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
              6.7881,
              46.405
            ],
            [
              6.7821,
              46.3785
            ],
            [
              6.7504,
              46.3455
            ],
            [
              6.8277,
              46.2695
            ],
            [
              6.7922,
         ...
```

### ECharts Option 骨架参考
请基于此结构（已剥离冗长写死的数据）生成配置。不要直接输出此骨架，而是要输出**包含真实数据和完整逻辑**的完整 `option` 对象：

```javascript
function createChart() {
  var chRoughLatitude = 47;
  option = {
    title: {
      text: 'Travel Routes'
    },
    geo: {
      map: 'ch',
      roam: true,
      aspectScale: Math.cos((chRoughLatitude * Math.PI) / 180),
      // nameProperty: 'name_en', // If using en name.
      label: {
        show: true,
        textBorderColor: '#fff',
        textBorderWidth: 2
      }
    },
    tooltip: {},
    series: [
      {
        type: 'graph',
        coordinateSystem: 'geo',
        data: [
          { name: 'a', value: [7.667821250000001, 46.791734269956265] },
          { name: 'b', value: [7.404848750000001, 46.516308805996054] },
          { name: 'c', value: [7.376673125000001, 46.24728858538375] },
          { name: 'd', value: [8.015320625000001, 46.39460918238572] },
          { name: 'e', value: [8.616400625, 46.7020608630855] },
          { name: 'f', value: [8.869981250000002, 46.37539345234199] },
          { name: 'g', value: [9.546196250000001, 46.58676648282309] },
          { name: 'h', value: [9.311399375, 47.182454114178896] },
          { name: 'i', value: [9.085994375000002, 47.55395822835779] },
          { name: 'j', value: [8.653968125000002, 47.47709530818285] },
          { name: 'k', value: [8.203158125000002, 47.44506909144329] }
        ],
        edges: [
          {
            source: 'a',
            target: 'b'
          },
          {
            source: 'b',
            target: 'c'
          },
          {
            source: 'c',
            target: 'd'
          },
          {
            source: 'd',
            target: 'e'
          },
          {
            source: 'e',
            target: 'f'
          },
          {
            source: 'f',
            target: 'g'
          },
          {
            source: 'g',
            target: 'h'
          },
          {
            source: 'h',
            target: 'i'
          },
          {
            source: 'i',
            target: 'j'
          },
          {
            source: 'j',
            target: 'k'
          }
        ],
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: 5,
        lineStyle: {
          color: '#718adbff',
          opacity: 1
        }
      }
    ]
  };
  myChart.setOption(option);
}
function fetchGeoJSON() {
  myChart.showLoading();
  $.get(ROOT_PATH + '/data/asset/geo/ch.geo.json', function (geoJSON) {
    echarts.registerMap('ch', geoJSON);
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
