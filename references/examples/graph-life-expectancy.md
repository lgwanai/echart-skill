# graph-life-expectancy

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph-life-expectancy
**Chart Type:** `graph`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

## Reference Code

```javascript
/*
title: Graph Life Expectancy
category: graph
titleCN: 预期寿命
difficulty: 7
*/
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
