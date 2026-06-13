# 预期寿命 / Graph Life Expectancy

**Category:** `graph`
**Example dir:** `graph-life-expectancy`
**Difficulty:** 7

## Template Match
- **graph/force.html** — Force Graph

## Option Code
```javascript
$.get(ROOT_PATH + '/data/asset/data/life-expectancy.json', function (rawData) {
  const series = [];
  rawData.counties.forEach(function (country) {
    const data = rawData.series.map(function (yearData) {
      const item = yearData.filter(function (item) {
        return item[3] === country;
      })[0];
      return {
        label: {
          show: +item[4] % 20 === 0 && +item[4] > 1940,
          position: 'top'
        },
        emphasis: {
          label: {
            show: true
          }
        },
        name: item[4],
        value: item
      };
    });
    var links = data.map(function (item, idx) {
      return {
        source: idx,
        target: idx + 1
      };
    });
    links.pop();
    series.push({
      name: country,
      type: 'graph',
      coordinateSystem: 'cartesian2d',
      data: data,
      links: links,
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: 5,
      legendHoverLink: false,
      lineStyle: {
        color: '#333'
      },
      itemStyle: {
        borderWidth: 1,
        borderColor: '#333'
      },
      label: {
        color: '#333',
        position: 'right'
      },
      symbolSize: 10,
      animationDelay: function (idx) {
        return idx * 100;
      }
    });
  });
  option = {
    visualMap: {
      show: false,
      min: 0,
      max: 100,
      dimension: 1
    },
    legend: {
      data: rawData.counties,
      selectedMode: 'single',
      right: 100
    },
    grid: {
      left: 0,
      bottom: 0,
      containLabel: true,
      top: 80
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'value',
      scale: true
    },
    toolbox: {
      feature: {
        dataZoom: {}
      }
    },
    dataZoom: {
      type: 'inside'
    },
    series: series
  };
  myChart.setOption(option);
});
```



## Key Points
- This is an official ECharts example from `graph-life-expectancy/main.js`
- Template data format: `{ nodes: [{id?, name, symbolSize?, category?, x?, y?}, ...], links: [{source, target, value?}, ...], categories?: [{name}, ...] }`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
