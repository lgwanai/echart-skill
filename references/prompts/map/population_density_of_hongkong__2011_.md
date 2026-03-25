## 图表类型：香港18区人口密度 （2011） (Population Density of HongKong (2011))

**生成指令**：你现在的任务是生成一个 ECharts 的 `option` 配置。请根据以下骨架代码和数据结构要求，结合用户的实际数据进行填充和修改，生成一份完整的图表配置参数。

### 外部数据结构分析
该图表需要特定的外部数据结构支撑。以下是下载后的数据结构示例，请将用户的真实数据映射为类似结构：

**数据文件 [/data/asset/geo/HK.json]**:
```json
数据是一个对象 (Object)。包含的顶层字段示例：type, features。数据截取示例：
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Central and Western",
        "ID_0": 102,
        "ID_1": 1,
        "ISO": "HKG"
      },
      "geometry": {
        "type": "MultiPolygon",
        "coordinates": [
          [
            [
              [
                114.113747,
                22.285694
              ],
              [
                114.113747,
                22.285418
              ],
            ...
```

### ECharts Option 骨架参考
请基于此结构（已剥离冗长写死的数据）生成配置。不要直接输出此骨架，而是要输出**包含真实数据和完整逻辑**的完整 `option` 对象：

```javascript
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/geo/HK.json', function (geoJson) {
  myChart.hideLoading();
  echarts.registerMap('HK', geoJson);
  myChart.setOption(
    (option = {
      title: {
        text: 'Population Density of Hong Kong （2011）',
        subtext: 'Data from Wikipedia',
        sublink:
          'http://zh.wikipedia.org/wiki/%E9%A6%99%E6%B8%AF%E8%A1%8C%E6%94%BF%E5%8D%80%E5%8A%83#cite_note-12'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}<br/>{c} (p / km2)'
      },
      toolbox: {
        show: true,
        orient: 'vertical',
        left: 'right',
        top: 'center',
        feature: {
          dataView: { readOnly: false },
          restore: {},
          saveAsImage: {}
        }
      },
      visualMap: {
        min: 800,
        max: 50000,
        text: ['High', 'Low'],
        realtime: false,
        calculable: true,
        inRange: {
          color: ['lightskyblue', 'yellow', 'orangered']
        }
      },
      series: [
        {
          name: '香港18区人口密度',
          type: 'map',
          map: 'HK',
          label: {
            show: true
          },
          data: [
            { name: '中西区', value: 20057.34 },
            { name: '湾仔', value: 15477.48 },
            { name: '东区', value: 31686.1 },
            { name: '南区', value: 6992.6 },
            { name: '油尖旺', value: 44045.49 },
            { name: '深水埗', value: 40689.64 },
            { name: '九龙城', value: 37659.78 },
            { name: '黄大仙', value: 45180.97 },
            { name: '观塘', value: 55204.26 },
            { name: '葵青', value: 21900.9 },
            { name: '荃湾', value: 4918.26 },
            { name: '屯门', value: 5881.84 },
            { name: '元朗', value: 4178.01 },
            { name: '北区', value: 2227.92 },
            { name: '大埔', value: 2180.98 },
            { name: '沙田', value: 9172.94 },
            { name: '西贡', value: 3368 },
            { name: '离岛', value: 806.98 }
          ],
          // 自定义名称映射
          nameMap: {
            'Central and Western': '中西区',
            Eastern: '东区',
            Islands: '离岛',
            'Kowloon City': '九龙城',
            'Kwai Tsing': '葵青',
            'Kwun Tong': '观塘',
            North: '北区',
            'Sai Kung': '西贡',
            'Sha Tin': '沙田',
            'Sham Shui Po': '深水埗',
            Southern: '南区',
            'Tai Po': '大埔',
            'Tsuen Wan': '荃湾',
            'Tuen Mun': '屯门',
            'Wan Chai': '湾仔',
            'Wong Tai Sin': '黄大仙',
            'Yau Tsim Mong': '油尖旺',
            'Yuen Long': '元朗'
          }
        }
      ]
    })
  );
});
```



### 🗺️ Map Fallback Rule (CRITICAL)
**如果用户需要展示的维度在本地 JS 中没有找到**（例如：细分城市维度、其他未涵盖的国家或地区），则**必须**使用 ECharts 百度地图扩展模式（即 `bmap` 模式，或称“AK 模式”）。
- **做法**：移除 `geo` 配置，改为使用 `bmap: { center: [lng, lat], zoom: 5, roam: true }`，并且所有的 map/scatter 系列必须指定 `coordinateSystem: 'bmap'`。
- **依赖**：此模式需要通过百度地图 AK 来渲染底图。生成时务必确保 `chart_generator.py` 能获取到配置好的 `BAIDU_AK`。
