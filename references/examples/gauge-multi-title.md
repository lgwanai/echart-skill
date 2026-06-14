# gauge-multi-title

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=gauge-multi-title

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
const gaugeData = [
  {
    value: 20,
    name: 'Good',
    title: {
      offsetCenter: ['-40%', '80%']
    },
    detail: {
      offsetCenter: ['-40%', '95%']
    }
  },
  {
    value: 40,
    name: 'Better',
    title: {
      offsetCenter: ['0%', '80%']
    },
    detail: {
      offsetCenter: ['0%', '95%']
    }
  },
  {
    value: 60,
    name: 'Perfect',
    title: {
      offsetCenter: ['40%', '80%']
    },
    detail: {
      offsetCenter: ['40%', '95%']
    }
  }
];
option = {
  series: [
    {
      type: 'gauge',
      anchor: {
        show: true,
        showAbove: true,
        size: 18,
        itemStyle: {
          color: '#FAC858'
        }
      },
      pointer: {
        icon: 'path://M2.9,0.7L2.9,0.7c1.4,0,2.6,1.2,2.6,2.6v115c0,1.4-1.2,2.6-2.6,2.6l0,0c-1.4,0-2.6-1.2-2.6-2.6V3.3C0.3,1.9,1.4,0.7,2.9,0.7z',
        width: 8,
        length: '80%',
        offsetCenter: [0, '8%']
      },
      progress: {
        show: true,
        overlap: true,
        roundCap: true
      },
      axisLine: {
        roundCap: true
      },
      data: gaugeData,
      title: {
        fontSize: 14
      },
      detail: {
        width: 40,
        height: 14,
        fontSize: 14,
        color: '#fff',
        backgroundColor: 'inherit',
        borderRadius: 3,
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
        data: gaugeData
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
