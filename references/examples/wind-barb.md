# 风向图 / Wind Barb

**Category:** `'custom, dataZoom'`
**Example dir:** `wind-barb`

## Template
⚠️ No template — use knowledge base
Data format: `N/A`

## Option Code
```javascript
$.getJSON(
  ROOT_PATH + '/data/asset/data/wind-barb-hobart.json',
  function (rawData) {
    const weatherIcons = {
      Showers: ROOT_PATH + '/data/asset/img/weather/showers_128.png',
      Sunny: ROOT_PATH + '/data/asset/img/weather/sunny_128.png',
      Cloudy: ROOT_PATH + '/data/asset/img/weather/cloudy_128.png'
    };
    const directionMap = {};
    // prettier-ignore
    ['W', 'WSW', 'SW', 'SSW', 'S', 'SSE', 'SE', 'ESE', 'E', 'ENE', 'NE', 'NNE', 'N', 'NNW', 'NW', 'WNW'].forEach(function (name, index) {
        directionMap[name] = Math.PI / 8 * index;
    });
    const data = rawData.data.map(function (entry) {
      return [entry.time, entry.windSpeed, entry.R, entry.waveHeight];
    });
    const weatherData = rawData.forecast.map(function (entry) {
      return [
        entry.localDate,
        0,
        weatherIcons[entry.skyIcon],
        entry.minTemp,
        entry.maxTemp
      ];
    });
    const dims = {
      time: 0,
      windSpeed: 1,
      R: 2,
      waveHeight: 3,
      weatherIcon: 2,
      minTemp: 3,
      maxTemp: 4
    };
    const arrowSize = 18;
    const weatherIconSize = 45;
    const renderArrow = function (param, api) {
      const point = api.coord([
        api.value(dims.time),
        api.value(dims.windSpeed)
      ]);
      return {
        type: 'path',
        shape: {
          pathData: 'M31 16l-15-15v9h-26v12h26v9z',
          x: -arrowSize / 2,
          y: -arrowSize / 2,
          width: arrowSize,
          height: arrowSize
        },
        rotation: directionMap[api.value(dims.R)],
        position: point,
        style: api.style({
          stroke: '#555',
          lineWidth: 1
        })
      };
    };
    const renderWeather = function (param, api) {
      const point = api.coord([
        api.value(dims.time) + (3600 * 24 * 1000) / 2,
        0
      ]);
      return {
        type: 'group',
        children: [
          {
            type: 'image',
            style: {
              image: api.value(
```

## Key Points
- Generate via: `scripts/build_template.py  -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
