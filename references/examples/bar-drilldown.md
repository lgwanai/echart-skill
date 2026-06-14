# bar-drilldown

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bar-drilldown

## Complete Code (copy-paste to HTML shell, replace data arrays with DuckDB real data)

```javascript
option = {
  xAxis: {
    data: ['Animals', 'Fruits', 'Cars']
  },
  yAxis: {},
  dataGroupId: '',
  animationDurationUpdate: 500,
  series: {
    type: 'bar',
    id: 'sales',
    data: [
      {
        value: 5,
        groupId: 'animals'
      },
      {
        value: 2,
        groupId: 'fruits'
      },
      {
        value: 4,
        groupId: 'cars'
      }
    ],
    universalTransition: {
      enabled: true,
      divideShape: 'clone'
    }
  }
};
const drilldownData = [
  {
    dataGroupId: 'animals',
    data: [
      ['Cats', 4],
      ['Dogs', 2],
      ['Cows', 1],
      ['Sheep', 2],
      ['Pigs', 1]
    ]
  },
  {
    dataGroupId: 'fruits',
    data: [
      ['Apples', 4],
      ['Oranges', 2]
    ]
  },
  {
    dataGroupId: 'cars',
    data: [
      ['Toyota', 4],
      ['Opel', 2],
      ['Volkswagen', 2]
    ]
  }
];
myChart.on('click', function (event) {
  if (event.data) {
    var subData = drilldownData.find(function (data) {
      return data.dataGroupId === event.data.groupId;
    });
    if (!subData) {
      return;
    }
    myChart.setOption({
      xAxis: {
        data: subData.data.map(function (item) {
          return item[0];
        })
      },
      series: {
        type: 'bar',
        id: 'sales',
        dataGroupId: subData.dataGroupId,
        data: subData.data.map(function (item) {
          return item[1];
        }),
        universalTransition: {
          enabled: true,
          divideShape: 'clone'
        }
      },
      graphic: [
        {
          type: 'text',
          left: 50,
          top: 20,
          style: {
            text: 'Back',
            fontSize: 18
          },
          onclick: function () {
            myChart.setOption(option);
          }
        }
      ]
    });
  }
});
```

## Data Arrays (replace with DuckDB real data)

- `data[0]`: `option = {
  xAxis: {...`
- `data[1]`: `{
    type: 'bar',
    id: 'sales',...`
- `data[2]`: `= [
  {
    dataGroupId: 'animals',...`
- `data[3]`: `},
  {
    dataGroupId: 'fruits',...`
- `data[4]`: `]
  },
  {
    dataGroupId: 'cars',...`

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
