# map-iceland-pie

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=map-iceland-pie

## ⚠️ Real Data REQUIRED

Code below contains **OFFICIAL DISPLAY DATA ONLY**. Agent MUST replace all `data: [...]` arrays with **real DuckDB data** before generating HTML.
Never output the official example data — it is for format reference only.

## Reference Code (REPLACE DATA ARRAYS BEFORE USE)

```javascript
/*
title: Pie Charts on GEO Map
category: map, pie
titleCN: 在地图上显示饼图
since: 5.4.0
difficulty: 5
*/
myChart.showLoading();
$.get(ROOT_PATH + '/data/asset/geo/iceland.geo.json', function (geoJSON) {
  echarts.registerMap('iceland', geoJSON);
  function randomPieSeries(center, radius) {
    const data = ['A', 'B', 'C', 'D'].map((t) => {
      return {
        value: Math.round(Math.random() * 100),
        name: 'Category ' + t
      };
    });
    return {
      type: 'pie',
      coordinateSystem: 'geo',
      tooltip: {
        formatter: '{b}: {c} ({d}%)'
      },
      label: {
        show: false
      },
      labelLine: {
        show: false
      },
      animationDuration: 0,
      radius,
      center,
      data
    };
  }
  option = {
    geo: {
      map: 'iceland',
      roam: true,
      aspectScale: Math.cos((65 * Math.PI) / 180),
      // nameProperty: 'name_en', // If using en name.
      itemStyle: {
        areaColor: '#e7e8ea'
      },
      emphasis: {
        label: { show: false }
      }
    },
    tooltip: {},
    legend: {},
    series: [
      randomPieSeries([-19.007740346534653, 64.1780281585128], 45),
      randomPieSeries([-17.204666089108912, 65.44804833928391], 25),
      randomPieSeries([-15.264995297029705, 64.8592208009264], 30),
      randomPieSeries(
        // it's also supported to use geo region name as center since v5.4.1
        +echarts.version.split('.').slice(0, 3).join('') > 540
          ? 'Vestfirðir'
          : // or you can only use the LngLat array
            [-13, 66],
        30
      )
    ]
  };
  myChart.hideLoading();
  myChart.setOption(option);
});
```

## Agent Workflow

1. Query DuckDB for real data
2. Replace each `data: [...]` array with real JSON data
3. Wrap in HTML shell with inline ECharts
4. Validate: `python scripts/validate_chart.py output.html`
