# gauge-ring

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=gauge-ring

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
const gaugeData = [
  {
    value: 20,
    name: 'Perfect',
    title: {
      offsetCenter: ['0%', '-30%']
    },
    detail: {
      valueAnimation: true,
      offsetCenter: ['0%', '-20%']
    }
  },
  {
    value: 40,
    name: 'Good',
    title: {
      offsetCenter: ['0%', '0%']
    },
    detail: {
      valueAnimation: true,
      offsetCenter: ['0%', '10%']
    }
  },
  {
    value: 60,
    name: 'Commonly',
    title: {
      offsetCenter: ['0%', '30%']
    },
    detail: {
      valueAnimation: true,
      offsetCenter: ['0%', '40%']
    }
  }
];
option = {
  series: [
    {
      type: 'gauge',
      startAngle: 90,
      endAngle: -270,
      pointer: {
        show: false
      },
      progress: {
        show: true,
        overlap: false,
        roundCap: true,
        clip: false,
        itemStyle: {
          borderWidth: 1,
          borderColor: '#464646'
        }
      },
      axisLine: {
        lineStyle: {
          width: 40
        }
      },
      splitLine: {
        show: false,
        distance: 0,
        length: 10
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        show: false,
        distance: 50
      },
      data: gaugeData,
      title: {
        fontSize: 14
      },
      detail: {
        width: 50,
        height: 14,
        fontSize: 14,
        color: 'inherit',
        borderColor: 'inherit',
        borderRadius: 20,
        borderWidth: 1,
        formatter: '{value}%'
      }
    }
  ]
};
setInterval(function () {
  gaugeData[0].value = +(Math.random() * 100).toFixed(2);
  gaugeData[1].value = +(Math.random() * 100).toFixed(2);
  gaugeData[2].value = +(Math.random() * 100).toFixed(2);
  myChart.setOption({
    series: [
      {
        data: gaugeData,
        pointer: {
          show: false
        }
      }
    ]
  });
}, 2000);
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
