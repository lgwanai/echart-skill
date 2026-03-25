## 图表类型：交通（SVG） (GEO SVG Traffic)

**生成指令**：你现在的任务是生成一个 ECharts 的 `option` 配置。请根据以下骨架代码和数据结构要求，结合用户的实际数据进行填充和修改，生成一份完整的图表配置参数。

### 图片资源提示
该图表需要加载以下类型的图片资源：
https://echarts.apache.org/examples/data/asset/geo/ksia-ext-plan-min.svg
请在生成代码时保留图片 URL 参数位置，并在最终输出时明确提示用户提供相应的图片资源 URL。

### ECharts Option 骨架参考
请基于此结构（已剥离冗长写死的数据）生成配置。不要直接输出此骨架，而是要输出**包含真实数据和完整逻辑**的完整 `option` 对象：

```javascript
$.get(ROOT_PATH + '/data/asset/geo/ksia-ext-plan-min.svg', function (svg) {
  echarts.registerMap('ksia-ext-plan', { svg: svg });
  option = {
    tooltip: {},
    geo: {
      map: 'ksia-ext-plan',
      roam: true,
      layoutCenter: ['50%', '50%'],
      layoutSize: '100%'
    },
    series: [
      {
        name: 'Route',
        type: 'lines',
        coordinateSystem: 'geo',
        geoIndex: 0,
        emphasis: {
          label: {
            show: false
          }
        },
        polyline: true,
        lineStyle: {
          color: '#c46e54',
          width: 0
        },
        effect: {
          show: true,
          period: 8,
          color: '#a10000',
          // constantSpeed: 80,
          trailLength: 0,
          symbolSize: [12, 30],
          symbol:
            'path://M87.1667 3.8333L80.5.5h-60l-6.6667 3.3333L.5 70.5v130l10 10h80l10 -10v-130zM15.5 190.5l15 -20h40l15 20zm75 -65l-15 5v35l15 15zm-80 0l15 5v35l-15 15zm65 0l15 -5v-40l-15 20zm-50 0l-15 -5v-40l15 20zm 65,-55 -15,25 c -15,-5 -35,-5 -50,0 l -15,-25 c 25,-15 55,-15 80,0 z'
        },
        z: 100,
        data: [
          {
            effect: {
              color: '#a10000',
              constantSpeed: 100,
              delay: 0
            },
            coords: [ /* 请使用用户的真实数据数组替换此处 */ ]
          },
          {
            effect: {
              color: '#00067d',
              constantSpeed: 80,
              delay: 0
            },
            coords: [ /* 请使用用户的真实数据数组替换此处 */ ]
          },
          {
            effect: {
              color: '#997405',
              constantSpeed: 60,
              delay: 0
            },
            coords: [ /* 请使用用户的真实数据数组替换此处 */ ]
          }
        ]
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
