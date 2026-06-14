# custom-ohlc

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=custom-ohlc

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
function splitData(rawData) {
  const categoryData = [];
  const values = [];
  for (var i = 0; i < rawData.length; i++) {
    categoryData.push(rawData[i][0]);
    rawData[i][0] = i;
    values.push(rawData[i]);
  }
  return {
    categoryData: categoryData,
    values: values
  };
}
function renderItem(params, api) {
  var xValue = api.value(0);
  var openPoint = api.coord([xValue, api.value(1)]);
  var closePoint = api.coord([xValue, api.value(2)]);
  var lowPoint = api.coord([xValue, api.value(3)]);
  var highPoint = api.coord([xValue, api.value(4)]);
  var halfWidth = api.size([1, 0])[0] * 0.35;
  var style = api.style({
    stroke: api.visual('color')
  });
  return {
    type: 'group',
    children: [
      {
        type: 'line',
        shape: {
          x1: lowPoint[0],
          y1: lowPoint[1],
          x2: highPoint[0],
          y2: highPoint[1]
        },
        style: style
      },
      {
        type: 'line',
        shape: {
          x1: openPoint[0],
          y1: openPoint[1],
          x2: openPoint[0] - halfWidth,
          y2: openPoint[1]
        },
        style: style
      },
      {
        type: 'line',
        shape: {
          x1: closePoint[0],
          y1: closePoint[1],
          x2: closePoint[0] + halfWidth,
          y2: closePoint[1]
        },
        style: style
      }
    ]
  };
}
$.get(ROOT_PATH + '/data/asset/data/stock-DJI.json', function (rawData) {
  var data = splitData(rawData);
  myChart.setOption(
    (option = {
      animation: false,
      legend: {
        bottom: 10,
        left: 'center',
        data: ['Dow-Jones index']
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        position: function (pos, params, el, elRect, size) {
          var obj = { top: 10 };
          obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
          return obj;
        }
      },
      axisPointer: {
        link: [{ xAxisIndex: 'all' }]
      },
      toolbox: {
        feature: {
          dataZoom: {
            yAxisIndex: false
          },
          brush: {
            type: ['lineX', 'clear']
          }
        }
      },
      grid: [
        {
          left: '10%',
          right: '8%',
          bottom: 150
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: data.categoryData,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          min: 'dataMin',
          max: 'dataMax',
          axisPointer: {
            z: 100
          }
        }
      ],
      yAxis: [
        {
          scale: true,
          splitArea: {
            show: true
          }
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          start: 98,
          end: 100,
          minValueSpan: 10
        },
        {
          show: true,
          type: 'slider',
          bottom: 60,
          start: 98,
          end: 100,
          minValueSpan: 10
        }
      ],
      series: [
        {
          name: 'Dow-Jones index',
          type: 'custom',
          renderItem: renderItem,
          dimensions: ['-', 'open', 'close', 'lowest', 'highest'],
          encode: {
            x: 0,
            y: [1, 2, 3, 4],
            tooltip: [1, 2, 3, 4]
          },
          data: data.values
        }
      ]
    }),
    true
  );
});
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `om: 10,
        left: 'center',...`

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
