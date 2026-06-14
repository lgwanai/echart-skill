# graph-life-expectancy

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=graph-life-expectancy
**Chart Type:** `graph`

## User Data Requirements

Columns needed: need **nodes** [{name,...}] + **links/edges** [{source,target}]

## Data Arrays — Replacement Guide

The code contains **0 data array(s)** to replace:

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

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
