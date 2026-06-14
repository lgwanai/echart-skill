# matrix-confusion

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=matrix-confusion

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
const label = {
  fontSize: 16,
  color: '#555'
};
option = {
  matrix: {
    x: {
      data: ['Positive', 'Negative'],
      label
    },
    y: {
      data: ['Positive', 'Negative'],
      label
    },
    top: 80,
    width: 600,
    left: 'center'
  },
  series: {
    type: 'custom',
    coordinateSystem: 'matrix',
    data: [
      ['Positive', 'Positive', 10],
      ['Positive', 'Negative', 2],
      ['Negative', 'Positive', 3],
      ['Negative', 'Negative', 5]
    ],
    label: {
      show: true,
      formatter: (params) => {
        const value = params.value[2];
        return (
          '{name|' +
          (params.value[0] === params.value[1] ? 'True ' : 'False ') +
          params.value[1] +
          '}\n{value|' +
          value +
          '}'
        );
      },
      rich: {
        name: {
          color: '#fff',
          backgroundColor: '#999',
          textBorderColor: '#333',
          padding: 5,
          fontSize: 18
        },
        value: {
          color: '#444',
          textBorderWidth: 0,
          padding: 5,
          fontSize: 16,
          align: 'center'
        }
      }
    },
    renderItem: function (params, api) {
      const x = api.value(0);
      const y = api.value(1);
      const rect = api.layout([x, y]).rect;
      return {
        type: 'rect',
        shape: {
          x: rect.x,
          y: rect.y,
          width: rect.width,
          height: rect.height
        },
        style: api.style({
          fill: x === y ? '#8f8' : '#f88'
        })
      };
    }
  },
  graphic: {
    elements: [
      {
        type: 'text',
        style: {
          text: 'True Class',
          fill: '#333',
          font: 'bold 24px serif',
          textAlign: 'center'
        },
        x: (window.innerWidth - 600) / 2 + (600 / 6) * 4,
        y: 40
      },
      {
        type: 'text',
        style: {
          text: 'Predicted Class',
          fill: '#333',
          font: 'bold 24px serif',
          textAlign: 'center'
        },
        x: (window.innerWidth - 600) / 2 - 50,
        y: 270,
        rotation: Math.PI / 2
      }
    ]
  }
};
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `;
option = {
  matrix: {
    x: {...`
- `data[1]`: `ve'],
      label
    },
    y: {...`
- `data[2]`: `m',
    coordinateSystem: 'matrix',...`

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
