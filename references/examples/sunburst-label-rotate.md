# sunburst-label-rotate

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sunburst-label-rotate

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
option = {
  silent: true,
  series: [
    {
      radius: ['15%', '80%'],
      type: 'sunburst',
      sort: undefined,
      emphasis: {
        focus: 'ancestor'
      },
      data: [
        {
          value: 8,
          children: [
            {
              value: 4,
              children: [
                {
                  value: 2
                },
                {
                  value: 1
                },
                {
                  value: 1
                },
                {
                  value: 0.5
                }
              ]
            },
            {
              value: 2
            }
          ]
        },
        {
          value: 4,
          children: [
            {
              children: [
                {
                  value: 2
                }
              ]
            }
          ]
        },
        {
          value: 4,
          children: [
            {
              children: [
                {
                  value: 2
                }
              ]
            }
          ]
        },
        {
          value: 3,
          children: [
            {
              children: [
                {
                  value: 1
                }
              ]
            }
          ]
        }
      ],
      label: {
        color: '#000',
        textBorderColor: '#fff',
        textBorderWidth: 2,
        formatter: function (param) {
          var depth = param.treePathInfo.length;
          if (depth === 2) {
            return 'radial';
          } else if (depth === 3) {
            return 'tangential';
          } else if (depth === 4) {
            return '0';
          }
          return '';
        }
      },
      levels: [
        {},
        {
          itemStyle: {
            color: '#CD4949'
          },
          label: {
            rotate: 'radial'
          }
        },
        {
          itemStyle: {
            color: '#F47251'
          },
          label: {
            rotate: 'tangential'
          }
        },
        {
          itemStyle: {
            color: '#FFC75F'
          },
          label: {
            rotate: 0
          }
        }
      ]
    }
  ]
};
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `focus: 'ancestor'
      },...`

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
