# bar-rich-text

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-rich-text

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
const weatherIcons = {
  Sunny: ROOT_PATH + '/data/asset/img/weather/sunny_128.png',
  Cloudy: ROOT_PATH + '/data/asset/img/weather/cloudy_128.png',
  Showers: ROOT_PATH + '/data/asset/img/weather/showers_128.png'
};
const seriesLabel = {
  show: true
};
option = {
  title: {
    text: 'Weather Statistics'
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {
    data: ['City Alpha', 'City Beta', 'City Gamma']
  },
  grid: {
    left: 100
  },
  toolbox: {
    show: true,
    feature: {
      saveAsImage: {}
    }
  },
  xAxis: {
    type: 'value',
    name: 'Days',
    axisLabel: {
      formatter: '{value}'
    }
  },
  yAxis: {
    type: 'category',
    inverse: true,
    data: ['Sunny', 'Cloudy', 'Showers'],
    axisLabel: {
      formatter: function (value) {
        return '{' + value + '| }\n{value|' + value + '}';
      },
      margin: 20,
      rich: {
        value: {
          lineHeight: 30,
          align: 'center'
        },
        Sunny: {
          height: 40,
          align: 'center',
          backgroundColor: {
            image: weatherIcons.Sunny
          }
        },
        Cloudy: {
          height: 40,
          align: 'center',
          backgroundColor: {
            image: weatherIcons.Cloudy
          }
        },
        Showers: {
          height: 40,
          align: 'center',
          backgroundColor: {
            image: weatherIcons.Showers
          }
        }
      }
    }
  },
  series: [
    {
      name: 'City Alpha',
      type: 'bar',
      data: [165, 170, 30],
      label: seriesLabel,
      markPoint: {
        symbolSize: 1,
        symbolOffset: [0, '50%'],
        label: {
          formatter: '{a|{a}\n}{b|{b} }{c|{c}}',
          backgroundColor: 'rgb(242,242,242)',
          borderColor: '#aaa',
          borderWidth: 1,
          borderRadius: 4,
          padding: [4, 10],
          lineHeight: 26,
          // shadowBlur: 5,
          // shadowColor: '#000',
          // shadowOffsetX: 0,
          // shadowOffsetY: 1,
          position: 'right',
          distance: 20,
          rich: {
            a: {
              align: 'center',
              color: '#fff',
              fontSize: 18,
              textShadowBlur: 2,
              textShadowColor: '#000',
              textShadowOffsetX: 0,
              textShadowOffsetY: 1,
              textBorderColor: '#333',
              textBorderWidth: 2
            },
            b: {
              color: '#333'
            },
            c: {
              color: '#ff8811',
              textBorderColor: '#000',
              textBorderWidth: 1,
              fontSize: 22
            }
          }
        },
        data: [
          { type: 'max', name: 'max days: ' },
          { type: 'min', name: 'min days: ' }
        ]
      }
    },
    {
      name: 'City Beta',
      type: 'bar',
      label: seriesLabel,
      data: [150, 105, 110]
    },
    {
      name: 'City Gamma',
      type: 'bar',
      label: seriesLabel,
      data: [220, 82, 63]
    }
  ]
};
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `pe: 'shadow'
    }
  },
  legend: {...`
- `data[1]`: `ype: 'category',
    inverse: true,...`
- `data[2]`: `'City Alpha',
      type: 'bar',...`
- `data[3]`: `}
          }
        },...`
- `data[4]`: `'bar',
      label: seriesLabel,...`

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
