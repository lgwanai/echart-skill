## 图表类型：使用线图绘制近100万纽约街道数据 (Use lines to draw 1 million New York streets)

**生成指令**：你现在的任务是生成一个 ECharts 的 `option` 配置。请根据以下骨架代码和数据结构要求，结合用户的实际数据进行填充和修改，生成一份完整的图表配置参数。

### ECharts Option 骨架参考
请基于此结构（已剥离冗长写死的数据）生成配置。不要直接输出此骨架，而是要输出**包含真实数据和完整逻辑**的完整 `option` 对象：

```javascript
var CHUNK_COUNT = 32;
var dataCount = 0;
function fetchData(idx) {
  if (idx >= CHUNK_COUNT) {
    return;
  }
  var dataURL =
    ROOT_PATH + '/data/asset/data/links-ny/links_ny_' + idx + '.bin';
  var xhr = new XMLHttpRequest();
  xhr.open('GET', dataURL, true);
  xhr.responseType = 'arraybuffer';
  xhr.onload = function (e) {
    var rawData = new Float32Array(this.response);
    var data = new Float64Array(rawData.length - 2);
    var offsetX = rawData[0];
    var offsetY = rawData[1];
    var off = 0;
    var addedDataCount = 0;
    for (var i = 2; i < rawData.length; ) {
      var count = rawData[i++];
      data[off++] = count;
      for (var k = 0; k < count; k++) {
        var x = rawData[i++] + offsetX;
        var y = rawData[i++] + offsetY;
        data[off++] = x;
        data[off++] = y;
        addedDataCount++;
      }
    }
    myChart.appendData({
      seriesIndex: 0,
      data: data
    });
    dataCount += addedDataCount;
    fetchData(idx + 1);
  };
  xhr.send();
}
option = {
  progressive: 20000,
  backgroundColor: '#111',
  geo: {
    center: [-74.04327099998152, 40.86737600240287],
    zoom: 360,
    map: 'world',
    roam: true,
    silent: true,
    itemStyle: {
      color: 'transparent',
      borderColor: 'rgba(255,255,255,0.1)',
      borderWidth: 1
    }
  },
  series: [
    {
      type: 'lines',
      coordinateSystem: 'geo',
      blendMode: 'lighter',
      dimensions: ['value'],
      data: new Float64Array(),
      polyline: true,
      large: true,
      lineStyle: {
        color: 'orange',
        width: 0.5,
        opacity: 0.3
      }
    }
  ]
};
fetchData(0);
```



### 🗺️ Map Fallback Rule (CRITICAL)
**如果用户需要展示的维度在本地 JS 中没有找到**（例如：细分城市维度、其他未涵盖的国家或地区），则**必须**使用 ECharts 百度地图扩展模式（即 `bmap` 模式，或称“AK 模式”）。
- **做法**：移除 `geo` 配置，改为使用 `bmap: { center: [lng, lat], zoom: 5, roam: true }`，并且所有的 map/scatter 系列必须指定 `coordinateSystem: 'bmap'`。
- **依赖**：此模式需要通过百度地图 AK 来渲染底图。生成时务必确保 `chart_generator.py` 能获取到配置好的 `BAIDU_AK`。
