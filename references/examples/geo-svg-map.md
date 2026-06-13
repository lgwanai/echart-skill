# 地图（SVG） / GEO SVG Map

**Category:** `map`
**Example dir:** `geo-svg-map`

## Template
- **geo/lines.html** — 
Data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`

## Option Code
```javascript
$.get(
  ROOT_PATH + '/data/asset/geo/Sicily_prehellenic_topographic_map.svg',
  function (svg) {
    echarts.registerMap('sicily', { svg: svg });
    option = {
      tooltip: {
        formatter: function (params) {
          console.log(params);
          return [
            params.name + ':',
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx',
            'xxxxxxxxxxxxxxxx'
          ].join('<br>');
        }
      },
      geo: [
        {
          map: 'sicily',
          roam: true,
          layoutCenter: ['50%', '50%'],
          layoutSize: '100%',
          selectedMode: 'single',
          tooltip: {
            show: true,
            confine: true,
            formatter: function (params) {
              return [
                'This is the introduction:',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx',
                'xxxxxxxxxxxxxxxxxxxxx'
              ].join('<br>');
            }
          },
          itemStyle: {
            color: undefined
          },
          emphasis: {
            label: {
              show: false
            }
          },
          select: {
            itemStyle: {
              color: '#b50205'
            },
            label: {
              show: false
            }
          },
          regions: [
            {
              name: 'route1',
              itemStyle: {
                borderWidth: 0
              },
              select: {
                itemStyle: {
                  color: '#b5280d',
                  borderWidth: 0
                }
              },
              tooltip: {
                position: 'right',
                alwaysShowContent: true,
              
```

## Key Points
- Generate via: `scripts/build_template.py geo/lines.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
