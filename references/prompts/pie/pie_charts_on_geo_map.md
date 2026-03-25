## 图表类型：在地图上显示饼图 (Pie Charts on GEO Map)

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
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/geo/iceland.geo.json', function (geoJSON) {
  echarts.registerMap('iceland', geoJSON);
  function randomPieSeries(center, radius) {
    const data = ['A', 'B', 'C', 'D'].map((t) => {
      return {
        value: Math.round(Math.random() * 100),
        name: 'Category ' + t
      };
    });
    return {
      type: 'pie',
      // CRITICAL WARNING: 'coordinateSystem: "geo"' is NOT SUPPORTED for 'pie' series in ECharts.
      // Do NOT use 'coordinateSystem: "geo"'. Instead, rely on 'center' with geo coordinates (requires ECharts v5.4.0+).
      tooltip: {
        formatter: '{b}: {c} ({d}%)'
      },
      label: {
        show: false
      },
      labelLine: {
        show: false
      },
      animationDuration: 0,
      radius,
      center,
      data
    };
  }
  option = {
    geo: {
      map: 'iceland',
      roam: true,
      aspectScale: Math.cos((65 * Math.PI) / 180),
      // nameProperty: 'name_en', // If using en name.
      itemStyle: {
        areaColor: '#e7e8ea'
      },
      emphasis: {
        label: { show: false }
      }
    },
    tooltip: {},
    legend: {},
    series: [
      randomPieSeries([-19.007740346534653, 64.1780281585128], 45),
      randomPieSeries([-17.204666089108912, 65.44804833928391], 25),
      randomPieSeries([-15.264995297029705, 64.8592208009264], 30),
      randomPieSeries(
        // it's also supported to use geo region name as center since v5.4.1
        +echarts.version.split('.').slice(0, 3).join('') > 540
          ? 'Vestfirðir'
          : // or you can only use the LngLat array
            [-13, 66],
        30
      )
    ]
  };
  myChart.hideLoading();
  myChart.setOption(option);
});
```

