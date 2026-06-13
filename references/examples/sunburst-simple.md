# 基础旭日图

**Category:** `sunburst`
**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sunburst-simple
**Template:** examples/sunburst-simple.html
**Data Format:** `[{name?: string, value?: number, itemStyle?: {}, children?: [...]}, ...]`
**Features:** emphasis/hover effects

## Official Option Code

```javascript
/*
title: Basic Sunburst
category: sunburst
titleCN: 基础旭日图
difficulty: 1
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
    // emphasis: {
    //     focus: 'ancestor'
    // },
    data: data,
    radius: [0, '90%'],
    label: {
      rotate: 'radial'
    }
  }
};
```

## Usage
- Build: `scripts/build_template.py examples/sunburst-simple.html -d data.json`
- Validate: `scripts/validate_chart.py output.html`
- Check `docs/CHART_DEBUG_LOG.md` for known issues
