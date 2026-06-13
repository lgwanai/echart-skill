# 圆角旭日图

**Category:** `sunburst`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sunburst-borderRadius
**Template:** examples/sunburst-borderRadius.html
**Data Format:** `[{name?: string, value?: number, itemStyle?: {}, children?: [...]}, ...]`

## Official Option Code

```javascript
/*
title: Sunburst with Rounded Corner
category: sunburst
titleCN: 圆角旭日图
difficulty: 2
*/
var data = [
  {
    name: 'Grandpa',
    children: [
      {
        name: 'Uncle Leo',
        value: 15,
        children: [
          {
            name: 'Cousin Jack',
            value: 2
          },
          {
            name: 'Cousin Mary',
            value: 5,
            children: [
              {
                name: 'Jackson',
                value: 2
              }
            ]
          },
          {
            name: 'Cousin Ben',
            value: 4
          }
        ]
      },
      {
        name: 'Father',
        value: 10,
        children: [
          {
            name: 'Me',
            value: 5
          },
          {
            name: 'Brother Peter',
            value: 1
          }
        ]
      }
    ]
  },
  {
    name: 'Nancy',
    children: [
      {
        name: 'Uncle Nike',
        children: [
          {
            name: 'Cousin Betty',
            value: 1
          },
          {
            name: 'Cousin Jenny',
            value: 2
          }
        ]
      }
    ]
  }
];
option = {
  series: {
    type: 'sunburst',
    data: data,
    radius: [60, '90%'],
    itemStyle: {
      borderRadius: 7,
      borderWidth: 2
    },
    label: {
      show: false
    }
  }
};
```

## Usage
- Build: `scripts/build_template.py examples/sunburst-borderRadius.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
