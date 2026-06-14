# scatterGL-gps

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatterGL-gps

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
var dataCount = 0;
var CHUNK_COUNT = 230;
// https://blog.openstreetmap.org/2012/04/01/bulk-gps-point-data/
function fetchData(idx) {
  if (idx >= CHUNK_COUNT) {
    return;
  }
  var dataURL = ROOT_PATH + '/data/asset/data/gps/gps_' + idx + '.bin';
  var xhr = new XMLHttpRequest();
  xhr.open('GET', dataURL, true);
  xhr.responseType = 'arraybuffer';
  xhr.onload = function (e) {
    var rawData = new Int32Array(this.response);
    var data = new Float32Array(rawData.length);
    var addedDataCount = rawData.length / 2;
    for (var i = 0; i < rawData.length; i += 2) {
      data[i] = rawData[i + 1] / 1e7;
      data[i + 1] = rawData[i] / 1e7;
    }
    myChart.appendData({
      seriesIndex: 0,
      data: data
    });
    fetchData(idx + 1);
  };
  xhr.send();
}
option = {
  backgroundColor: '#000',
  title: {
    text: '10000000 GPS Points',
    left: 'center',
    textStyle: {
      color: '#fff'
    }
  },
  geo: {
    map: 'world',
    roam: true,
    label: {
      emphasis: {
        show: false
      }
    },
    silent: true,
    itemStyle: {
      normal: {
        areaColor: '#323c48',
        borderColor: '#111'
      },
      emphasis: {
        areaColor: '#2a333d'
      }
    }
  },
  series: [
    {
      name: 'å¼±',
      type: 'scatterGL',
      progressive: 1e6,
      coordinateSystem: 'geo',
      symbolSize: 1,
      zoomScale: 0.002,
      blendMode: 'lighter',
      large: true,
      itemStyle: {
        color: 'rgb(20, 15, 2)'
      },
      postEffect: {
        enable: true
      },
      silent: true,
      dimensions: ['lng', 'lat'],
      data: new Float32Array()
    }
  ]
};
fetchData(0);
```

## HTML Shell
```html
<!DOCTYPE html><html lang="zh-CN">
<head><meta charset="utf-8"><title>TITLE</title>
<script>/* ECHARTS_INLINE */</script>
<style>body{margin:0;padding:16px;font-family:sans-serif}#main{width:100%;height:600px}</style>
</head><body><div id="main"></div><script>
var chart = echarts.init(document.getElementById("main"));
// PASTE COMPLETE CODE HERE, replace data arrays with DuckDB real data
chart.setOption(option);
window.addEventListener("resize",function(){chart.resize();});
</script></body></html>
```
