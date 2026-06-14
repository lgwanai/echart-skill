# geo-seatmap-flight

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=geo-seatmap-flight

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
$.get(ROOT_PATH + '/data/asset/geo/flight-seats.svg', function (svg) {
  echarts.registerMap('flight-seats', { svg: svg });
  const takenSeatNames = ['26E', '26D', '26C', '25D', '23C', '21A', '20F'];
  option = {
    tooltip: {},
    geo: {
      map: 'flight-seats',
      roam: true,
      selectedMode: 'multiple',
      layoutCenter: ['50%', '50%'],
      layoutSize: '95%',
      tooltip: {
        show: true
      },
      itemStyle: {
        color: '#fff'
      },
      emphasis: {
        itemStyle: {
          color: undefined,
          borderColor: 'green',
          borderWidth: 2
        },
        label: {
          show: false
        }
      },
      select: {
        itemStyle: {
          color: 'green'
        },
        label: {
          show: false,
          textBorderColor: '#fff',
          textBorderWidth: 2
        }
      },
      regions: makeTakenRegions(takenSeatNames)
    }
  };
  function makeTakenRegions(takenSeatNames) {
    var regions = [];
    for (var i = 0; i < takenSeatNames.length; i++) {
      regions.push({
        name: takenSeatNames[i],
        silent: true,
        itemStyle: {
          color: '#bf0e08'
        },
        emphasis: {
          itemStyle: {
            borderColor: '#aaa',
            borderWidth: 1
          }
        },
        select: {
          itemStyle: {
            color: '#bf0e08'
          }
        }
      });
    }
    return regions;
  }
  myChart.setOption(option);
  // Get selected seats.
  myChart.on('geoselectchanged', function (params) {
    const selectedNames = params.allSelected[0].name.slice();
    // Remove taken seats.
    for (var i = selectedNames.length - 1; i >= 0; i--) {
      if (takenSeatNames.indexOf(selectedNames[i]) >= 0) {
        selectedNames.splice(i, 1);
      }
    }
    console.log('selected', selectedNames);
  });
});
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
