# lines-ny

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=lines-ny
**Chart Type:** `lines`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

## Reference Code

```javascript
/*
title: Use lines to draw 1 million New York streets
titleCN: 使用线图绘制近100万纽约街道数据
category: 'map, lines'
shotDelay: 1000
*/
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
