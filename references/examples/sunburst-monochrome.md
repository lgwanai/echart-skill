# sunburst-monochrome

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sunburst-monochrome

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
const item1 = {
  color: '#F54F4A'
};
const item2 = {
  color: '#FF8C75'
};
const item3 = {
  color: '#FFB499'
};
const data = [
  {
    children: [
      {
        value: 5,
        children: [
          {
            value: 1,
            itemStyle: item1
          },
          {
            value: 2,
            children: [
              {
                value: 1,
                itemStyle: item2
              }
            ]
          },
          {
            children: [
              {
                value: 1
              }
            ]
          }
        ],
        itemStyle: item1
      },
      {
        value: 10,
        children: [
          {
            value: 6,
            children: [
              {
                value: 1,
                itemStyle: item1
              },
              {
                value: 1
              },
              {
                value: 1,
                itemStyle: item2
              },
              {
                value: 1
              }
            ],
            itemStyle: item3
          },
          {
            value: 2,
            children: [
              {
                value: 1
              }
            ],
            itemStyle: item3
          },
          {
            children: [
              {
                value: 1,
                itemStyle: item2
              }
            ]
          }
        ],
        itemStyle: item1
      }
    ],
    itemStyle: item1
  },
  {
    value: 9,
    children: [
      {
        value: 4,
        children: [
          {
            value: 2,
            itemStyle: item2
          },
          {
            children: [
              {
                value: 1,
                itemStyle: item1
              }
            ]
          }
        ],
        itemStyle: item1
      },
      {
        children: [
          {
            value: 3,
            children: [
              {
                value: 1
              },
              {
                value: 1,
                itemStyle: item2
              }
            ]
          }
        ],
        itemStyle: item3
      }
    ],
    itemStyle: item2
  },
  {
    value: 7,
    children: [
      {
        children: [
          {
            value: 1,
            itemStyle: item3
          },
          {
            value: 3,
            children: [
              {
                value: 1,
                itemStyle: item2
              },
              {
                value: 1
              }
            ],
            itemStyle: item2
          },
          {
            value: 2,
            children: [
              {
                value: 1
              },
              {
                value: 1,
                itemStyle: item1
              }
            ],
            itemStyle: item1
          }
        ],
        itemStyle: item3
      }
    ],
    itemStyle: item1
  },
  {
    children: [
      {
        value: 6,
        children: [
          {
            value: 1,
            itemStyle: item2
          },
          {
            value: 2,
            children: [
              {
                value: 2,
                itemStyle: item2
              }
            ],
            itemStyle: item1
          },
          {
            value: 1,
            itemStyle: item3
          }
        ],
        itemStyle: item3
      },
      {
        value: 3,
        children: [
          {
            value: 1
          },
          {
            children: [
              {
                value: 1,
                itemStyle: item2
              }
            ]
          },
          {
            value: 1
          }
        ],
        itemStyle: item3
      }
    ],
    itemStyle: item1
  }
];
option = {
  series: {
    radius: ['15%', '80%'],
    type: 'sunburst',
    sort: undefined,
    emphasis: {
      focus: 'ancestor'
    },
    data: data,
    label: {
      rotate: 'radial'
    },
    levels: [],
    itemStyle: {
      color: '#ddd',
      borderWidth: 2
    }
  }
};
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
