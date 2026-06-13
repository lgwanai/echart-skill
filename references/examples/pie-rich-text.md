# 富文本标签 / Pie Special Label

**Category:** `'pie, rich'`
**Example dir:** `pie-rich-text`

## Template
- **pie/basic.html** — Pie
Data format: `[{name: string, value: number}, ...]`

## Option Code
```javascript
const weatherIcons = {
  Sunny: ROOT_PATH + '/data/asset/img/weather/sunny_128.png',
  Cloudy: ROOT_PATH + '/data/asset/img/weather/cloudy_128.png',
  Showers: ROOT_PATH + '/data/asset/img/weather/showers_128.png'
};
option = {
  title: {
    text: 'Weather Statistics',
    subtext: 'Fake Data',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b} : {c} ({d}%)'
  },
  legend: {
    bottom: 10,
    left: 'center',
    data: ['CityA', 'CityB', 'CityD', 'CityC', 'CityE']
  },
  series: [
    {
      type: 'pie',
      radius: '65%',
      center: ['50%', '50%'],
      selectedMode: 'single',
      data: [
        {
          value: 1548,
          name: 'CityE',
          label: {
            formatter: [
              '{title|{b}}{abg|}',
              '  {weatherHead|Weather}{valueHead|Days}{rateHead|Percent}',
              '{hr|}',
              '  {Sunny|}{value|202}{rate|55.3%}',
              '  {Cloudy|}{value|142}{rate|38.9%}',
              '  {Showers|}{value|21}{rate|5.8%}'
            ].join('\n'),
            backgroundColor: '#eee',
            borderColor: '#777',
            borderWidth: 1,
            borderRadius: 4,
            rich: {
              title: {
                color: '#eee',
                align: 'center'
              },
              abg: {
                backgroundColor: '#333',
                width: '100%',
                align: 'right',
                height: 25,
                borderRadius: [4, 4, 0, 0]
              },
              Sunny: {
                height: 30,
                align: 'left',
                backgroundColor: {
                  image: weatherIcons.Sunny
                }
              },
              Cloudy: {
                height: 30,
                align: 'left',
                backgroundColor: {
                  image: weatherIcons.Cloudy
                }
              },
              Showers: {
                height: 30,
                align: 'left',
 
```

## Key Points
- Generate via: `scripts/build_template.py pie/basic.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
