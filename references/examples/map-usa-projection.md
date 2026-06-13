# 自定义地图投影 / USA Choropleth Map with Projection

**Category:** `map`
**Example dir:** `map-usa-projection`

## Template
- **map/basic.html** — Map
Data format: `[{name: string, value: number}, ...]`

## Option Code
```javascript
myChart.showLoading();
$.when(
  $.get(ROOT_PATH + '/data/asset/geo/USA.json'),
  $.getScript(CDN_PATH + 'd3-array@2.8.0/dist/d3-array.js'),
  $.getScript(CDN_PATH + 'd3-geo@2.0.1/dist/d3-geo.js')
).done(function (res) {
  const usaJson = res[0];
  const projection = d3.geoAlbersUsa();
  myChart.hideLoading();
  echarts.registerMap('USA', usaJson);
  option = {
    title: {
      text: 'USA Population Estimates (2012)',
      subtext: 'Data from www.census.gov',
      sublink: 'http://www.census.gov/popest/data/datasets.html',
      left: 'right'
    },
    tooltip: {
      trigger: 'item',
      showDelay: 0,
      transitionDuration: 0.2
    },
    visualMap: {
      left: 'right',
      min: 500000,
      max: 38000000,
      inRange: {
        color: [
          '#313695',
          '#4575b4',
          '#74add1',
          '#abd9e9',
          '#e0f3f8',
          '#ffffbf',
          '#fee090',
          '#fdae61',
          '#f46d43',
          '#d73027',
          '#a50026'
        ]
      },
      text: ['High', 'Low'],
      calculable: true
    },
    toolbox: {
      show: true,
      //orient: 'vertical',
      left: 'left',
      top: 'top',
      feature: {
        dataView: { readOnly: false },
        restore: {},
        saveAsImage: {}
      }
    },
    series: [
      {
        name: 'USA PopEstimates',
        type: 'map',
        map: 'USA',
        projection: {
          project: function (point) {
            return projection(point);
          },
          unproject: function (point) {
            return projection.invert(point);
          }
        },
        emphasis: {
          label: {
            show: true
          }
        },
        data: [
          { name: 'Alabama', value: 4822023 },
          { name: 'Alaska', value: 731449 },
          { name: 'Arizona', value: 6553255 },
          { name: 'Arkansas', value: 2949131 },
          { name: 'California', value: 38041430 },
          { name: 'Colorado', value: 5187582 },
       
```

## Key Points
- Generate via: `scripts/build_template.py map/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
