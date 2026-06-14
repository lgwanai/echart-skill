# bar-breaks-simple

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-breaks-simple

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
var _currentAxisBreaks = [
  {
    start: 5000,
    end: 100000,
    gap: '1.5%'
  },
  {
    // `start` and `end` are also used as the identifier for a certain axis break.
    start: 105000,
    end: 3100000,
    gap: '1.5%'
  }
];
option = {
  title: {
    text: 'Bar Chart with Axis Breaks',
    subtext: 'Click the break area to expand it',
    left: 'center',
    textStyle: {
      fontSize: 20
    },
    subtextStyle: {
      color: '#175ce5',
      fontSize: 15,
      fontWeight: 'bold'
    }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {},
  grid: {
    top: 120
  },
  xAxis: [
    {
      type: 'category',
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    }
  ],
  yAxis: [
    {
      type: 'value',
      breaks: _currentAxisBreaks,
      breakArea: {
        itemStyle: {
          opacity: 1
        },
        zigzagZ: 200
      }
    }
  ],
  series: [
    {
      name: 'Data A',
      type: 'bar',
      emphasis: {
        focus: 'series'
      },
      data: [1500, 2032, 2001, 3154, 2190, 4330, 2410]
    },
    {
      name: 'Data B',
      type: 'bar',
      emphasis: {
        focus: 'series'
      },
      data: [1200, 1320, 1010, 1340, 900, 2300, 2100]
    },
    {
      name: 'Data C',
      type: 'bar',
      emphasis: {
        focus: 'series'
      },
      data: [103200, 100320, 103010, 102340, 103900, 103300, 103200]
    },
    {
      name: 'Data D',
      type: 'bar',
      data: [3106212, 3102118, 3102643, 3104631, 3106679, 3100130, 3107022],
      emphasis: {
        focus: 'series'
      }
    }
  ]
};

function initAxisBreakInteraction() {
  myChart.on('axisbreakchanged', function (params) {
    updateCollapseButton(params);
  });
  myChart.on('click', function (params) {
    if (params.name === 'collapseAxisBreakBtn') {
      collapseAxisBreak();
    }
  });
  function updateCollapseButton(params) {
    // If there is any axis break expanded, we need to show the collapse button.
    var needReset = false;
    for (let i = 0; i < params.breaks.length; i++) {
      const changedBreakItem = params.breaks[i];
      if (changedBreakItem.isExpanded) {
        needReset = true;
        break;
      }
    }
    myChart.setOption({
      // Draw the collapse button.
      graphic: [
        {
          elements: [
            {
              type: 'rect',
              ignore: !needReset,
              name: 'collapseAxisBreakBtn',
              top: 5,
              left: 5,
              shape: { r: 3, width: 140, height: 24 },
              style: { fill: '#eee', stroke: '#999', lineWidth: 1 },
              textContent: {
                type: 'text',
                style: {
                  text: 'Collapse Axis Breaks',
                  fontSize: 13,
                  fontWeight: 'bold'
                }
              },
              textConfig: { position: 'inside' }
            }
          ]
        }
      ]
    });
  }
  function collapseAxisBreak() {
    myChart.dispatchAction({
      type: 'collapseAxisBreak',
      yAxisIndex: 0,
      breaks: _currentAxisBreaks
    });
  }
} // End of initAxisBreakInteraction
setTimeout(initAxisBreakInteraction, 0);
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `: [
    {
      type: 'category',...`
- `data[1]`: `focus: 'series'
      },...`
- `data[2]`: `focus: 'series'
      },...`
- `data[3]`: `focus: 'series'
      },...`
- `data[4]`: `ame: 'Data D',
      type: 'bar',...`

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
