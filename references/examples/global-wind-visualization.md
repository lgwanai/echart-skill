# Global wind visualization / Global wind visualization

**Category:** `flowGL`
**Example dir:** `global-wind-visualization`

## Template
⚠️ No template — use knowledge base
Data format: `N/A`

## Option Code
```javascript
$.getJSON(ROOT_PATH + '/data-gl/asset/data/winds.json', function (windData) {
  var data = [];
  var p = 0;
  var maxMag = 0;
  var minMag = Infinity;
  for (var j = 0; j < windData.ny; j++) {
    for (var i = 0; i <= windData.nx; i++) {
      // Continuous data.
      var p = (i % windData.nx) + j * windData.nx;
      var vx = windData.data[p][0];
      var vy = windData.data[p][1];
      var mag = Math.sqrt(vx * vx + vy * vy);
      // æ°æ®æ¯ä¸ä¸ªä¸ç»´æ°ç»
      // [ [ç»åº¦, ç»´åº¦ï¼åéç»åº¦æ¹åçå¼ï¼åéç»´åº¦æ¹åçå¼] ]
      data.push([
        (i / windData.nx) * 360 - 180,
        (j / windData.ny) * 180 - 90,
        vx,
        vy,
        mag
      ]);
      maxMag = Math.max(mag, maxMag);
      minMag = Math.min(mag, minMag);
    }
  }
  myChart.setOption(
    (option = {
      backgroundColor: '#001122',
      visualMap: {
        left: 'right',
        min: minMag,
        max: maxMag,
        dimension: 4,
        inRange: {
          // color: ['green', 'yellow', 'red']
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
        realtime: false,
        calculable: true,
        textStyle: {
          color: '#fff'
        }
      },
      bmap: {
        center: [0, 0],
        zoom: 1,
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
             
```

## Key Points
- Generate via: `scripts/build_template.py  -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
