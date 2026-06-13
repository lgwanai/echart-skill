# 使用自定义系列绘制风场 / Use custom series to draw wind vectors

**Category:** `custom`
**Example dir:** `custom-wind`

## Template
- **custom/error-bar.html** — Error Bar
Data format: `[[xIdx, val, lowVal, highVal], ...]`

## Option Code
```javascript
function shuffle(array) {
  // https://stackoverflow.com/questions/2450954/how-to-randomize-shuffle-a-javascript-array
  var currentIndex = array.length;
  var temporaryValue;
  var randomIndex;
  // While there remain elements to shuffle...
  while (0 !== currentIndex) {
    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;
    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }
  return array;
}
$.getJSON(ROOT_PATH + '/data-gl/asset/data/winds.json', function (windData) {
  var p = 0;
  var maxMag = 0;
  var minMag = Infinity;
  var data = [];
  for (var j = 0; j < windData.ny; j++) {
    for (var i = 0; i < windData.nx; i++, p++) {
      var vx = windData.data[p][0];
      var vy = windData.data[p][1];
      var mag = Math.sqrt(vx * vx + vy * vy);
      // 数据是一个一维数组
      // [ [经度, 维度，向量经度方向的值，向量维度方向的值] ]
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
  shuffle(data);
  myChart.setOption(
    (option = {
      backgroundColor: '#333',
      visualMap: {
        left: 'center',
        min: minMag,
        max: maxMag,
        dimension: 4,
        inRange: {
          // prettier-ignore
          color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
        },
        calculable: true,
        textStyle: {
          color: '#fff'
        },
        orient: 'horizontal'
      },
      geo: {
        map: 'world',
        left: 0,
        right: 0,
        top: 0,
        zoom: 1,
        silent: true,
        roam: true,
        itemStyle: {
          areaColor: '#323c48',
          borderColor: '#111'
        }
      },
      seri
```

## Key Points
- Generate via: `scripts/build_template.py custom/error-bar.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
