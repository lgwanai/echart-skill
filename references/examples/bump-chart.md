# bump-chart

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=bump-chart
**Chart Type:** `line`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: need **time/category** + **value** columns
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

## Reference Code

```javascript
/*
title: Bump Chart (Ranking)
category: line
titleCN: 凹凸图
difficulty: 2
*/
const names = [
  'Orange',
  'Tomato',
  'Apple',
  'Sakana',
  'Banana',
  'Iwashi',
  'Snappy Fish',
  'Lemon',
  'Pasta'
];
const years = ['2001', '2002', '2003', '2004', '2005', '2006'];
const shuffle = (array) => {
  let currentIndex = array.length;
  let randomIndex = 0;
  while (currentIndex > 0) {
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;
    [array[currentIndex], array[randomIndex]] = [
      array[randomIndex],
      array[currentIndex]
    ];
  }
  return array;
};
const generateRankingData = () => {
  const map = new Map();
  const defaultRanking = Array.from({ length: names.length }, (_, i) => i + 1);
  for (const _ of years) {
    const shuffleArray = shuffle(defaultRanking);
    names.forEach((name, i) => {
      map.set(name, (map.get(name) || []).concat(shuffleArray[i]));
    });
  }
  return map;
};
const generateSeriesList = () => {
  const seriesList = [];
  const rankingMap = generateRankingData();
  rankingMap.forEach((data, name) => {
    const series = {
      name,
      symbolSize: 20,
      type: 'line',
      smooth: true,
      emphasis: {
        focus: 'series'
      },
      endLabel: {
        show: true,
        formatter: '{a}',
        distance: 20
      },
      lineStyle: {
        width: 4
      },
      data
    };
    seriesList.push(series);
  });
  return seriesList;
};
option = {
  title: {
    text: 'Bump Chart (Ranking)'
  },
  tooltip: {
    trigger: 'item'
  },
  grid: {
    left: 30,
    right: 110,
    bottom: 30,
    containLabel: true
  },
  toolbox: {
    feature: {
      saveAsImage: {}
    }
  },
  xAxis: {
    type: 'category',
    splitLine: {
      show: true
    },
    axisLabel: {
      margin: 30,
      fontSize: 16
    },
    boundaryGap: false,
    data: years
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      margin: 30,
      fontSize: 16,
      formatter: '#{value}'
    },
    inverse: true,
    interval: 1,
    min: 1,
    max: names.length
  },
  series: generateSeriesList()
};
```
