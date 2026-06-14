# sunburst-label-rotate

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sunburst-label-rotate

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

**1 data arrays** to replace:
- `data[0]`: `data: [
        {
          value: 8,
          children: [
            {
      ...`

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Sunburst Label Rotate
category: sunburst
titleCN: 旭日图标签旋转
difficulty: 2
*/
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

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
