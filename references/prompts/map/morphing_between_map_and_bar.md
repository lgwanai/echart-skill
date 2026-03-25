## 图表类型：地图柱状图变形动画 (Morphing between Map and Bar)

**生成指令**：你现在的任务是生成一个 ECharts 的 `option` 配置。请根据以下骨架代码和数据结构要求，结合用户的实际数据进行填充和修改，生成一份完整的图表配置参数。

### 外部数据结构分析
该图表需要特定的外部数据结构支撑。以下是下载后的数据结构示例，请将用户的真实数据映射为类似结构：

**数据文件 [/data/asset/geo/USA.json]**:
```json
数据是一个对象 (Object)。包含的顶层字段示例：type, features。数据截取示例：
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "01",
      "properties": {
        "name": "Alabama"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -87.359296,
              35.00118
            ],
            [
              -85.606675,
              34.984749
            ],
            [
              -85.431413,
              34.124869
            ],
            [
           ...
```

### ECharts Option 骨架参考
请基于此结构（已剥离冗长写死的数据）生成配置。不要直接输出此骨架，而是要输出**包含真实数据和完整逻辑**的完整 `option` 对象：

```javascript
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/geo/USA.json', function (usaJson) {
  myChart.hideLoading();
  echarts.registerMap('USA', usaJson, {
    Alaska: {
      // 把阿拉斯加移到美国主大陆左下方
      left: -131,
      top: 25,
      width: 15
    },
    Hawaii: {
      left: -110,
      top: 28,
      width: 5
    },
    'Puerto Rico': {
      // 波多黎各
      left: -76,
      top: 26,
      width: 2
    }
  });
  var data = [ /* 请使用用户的真实数据数组替换此处 */ ];
  data.sort(function (a, b) {
    return a.value - b.value;
  });
  const mapOption = {
    visualMap: {
      left: 'right',
      min: 500000,
      max: 38000000,
      inRange: {
        // prettier-ignore
        color: [ /* 请使用用户的真实数据数组替换此处 */ ]
      },
      text: ['High', 'Low'],
      calculable: true
    },
    series: [
      {
        id: 'population',
        type: 'map',
        roam: true,
        map: 'USA',
        animationDurationUpdate: 1000,
        universalTransition: true,
        data: data
      }
    ]
  };
  const barOption = {
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      axisLabel: {
        rotate: 30
      },
      data: data.map(function (item) {
        return item.name;
      })
    },
    animationDurationUpdate: 1000,
    series: {
      type: 'bar',
      id: 'population',
      data: data.map(function (item) {
        return item.value;
      }),
      universalTransition: true
    }
  };
  let currentOption = mapOption;
  myChart.setOption(mapOption);
  setInterval(function () {
    currentOption = currentOption === mapOption ? barOption : mapOption;
    myChart.setOption(currentOption, true);
  }, 2000);
});
```



### 🗺️ Map Fallback Rule (CRITICAL)
**如果用户需要展示的维度在本地 JS 中没有找到**（例如：细分城市维度、其他未涵盖的国家或地区），则**必须**使用 ECharts 百度地图扩展模式（即 `bmap` 模式，或称“AK 模式”）。
- **做法**：移除 `geo` 配置，改为使用 `bmap: { center: [lng, lat], zoom: 5, roam: true }`，并且所有的 map/scatter 系列必须指定 `coordinateSystem: 'bmap'`。
- **依赖**：此模式需要通过百度地图 AK 来渲染底图。生成时务必确保 `chart_generator.py` 能获取到配置好的 `BAIDU_AK`。
