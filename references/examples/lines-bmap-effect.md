# 北京公交路线 - 线特效 / Bus Lines of Beijing - Line Effect

**Category:** `'map, lines'`
**Example dir:** `lines-bmap-effect`

## Template
- **lines/flights.html** — Lines
Data format: `{ geoCoordMap: {"name": [lng,lat]}, flights: [[fromName, toName], ...] }`

## Option Code
```javascript
$.get(ROOT_PATH + '/data/asset/data/lines-bus.json', function (data) {
  let hStep = 300 / (data.length - 1);
  let busLines = [].concat.apply(
    [],
    data.map(function (busLine, idx) {
      let prevPt = [];
      let points = [];
      for (let i = 0; i < busLine.length; i += 2) {
        let pt = [busLine[i], busLine[i + 1]];
        if (i > 0) {
          pt = [prevPt[0] + pt[0], prevPt[1] + pt[1]];
        }
        prevPt = pt;
        points.push([pt[0] / 1e4, pt[1] / 1e4]);
      }
      return {
        coords: points,
        lineStyle: {
          normal: {
            color: echarts.color.modifyHSL('#5A94DF', Math.round(hStep * idx))
          }
        }
      };
    })
  );
  myChart.setOption(
    (option = {
      backgroundColor: 'transparent',
      bmap: {
        center: [116.46, 39.92],
        zoom: 10,
        roam: true,
        mapStyle: {
          styleJson: [
            {
              featureType: 'water',
              elementType: 'all',
              stylers: {
                color: '#031628'
              }
            },
            {
              featureType: 'land',
              elementType: 'geometry',
              stylers: {
                color: '#000102'
              }
            },
            {
              featureType: 'highway',
              elementType: 'all',
              stylers: {
                visibility: 'off'
              }
            },
            {
              featureType: 'arterial',
              elementType: 'geometry.fill',
              stylers: {
                color: '#000000'
              }
            },
            {
              featureType: 'arterial',
              elementType: 'geometry.stroke',
              stylers: {
                color: '#0b3d51'
              }
            },
            {
              featureType: 'local',
              elementType: 'geometry',
              stylers: {
                color: '#000000'
              }
            },
            {
   
```

## Key Points
- Generate via: `scripts/build_template.py lines/flights.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
