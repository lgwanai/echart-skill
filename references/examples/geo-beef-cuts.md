# geo-beef-cuts

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=geo-beef-cuts
**Chart Type:** `map`

## User Data Requirements

Columns needed: need **region name** + **value** columns

## Data Arrays — Replacement Guide

The code contains **1 data array(s)** to replace:

### data[0]: `unknown`
- **Format**: `[{...},...] — object array`
- **Location**: `data: [
          { name: 'Queue', value: 15 },
          { name: 'Langue', value: 35 },
          {...`
- **Replace with**: real data from DuckDB in the same format

## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: GEO Beef Cuts
category: map
titleCN: 庖丁解牛
*/
$.get(ROOT_PATH + '/data/asset/geo/Beef_cuts_France.svg', function (svg) {
  echarts.registerMap('Beef_cuts_France', { svg: svg });
  option = {
    tooltip: {},
    visualMap: {
      left: 'center',
      bottom: '10%',
      min: 5,
      max: 100,
      orient: 'horizontal',
      text: ['', 'Price'],
      realtime: true,
      calculable: true,
      inRange: {
        color: ['#dbac00', '#db6e00', '#cf0000']
      }
    },
    series: [
      {
        name: 'French Beef Cuts',
        type: 'map',
        map: 'Beef_cuts_France',
        roam: true,
        emphasis: {
          label: {
            show: false
          }
        },
        selectedMode: false,
        data: [
          { name: 'Queue', value: 15 },
          { name: 'Langue', value: 35 },
          { name: 'Plat de joue', value: 15 },
          { name: 'Gros bout de poitrine', value: 25 },
          { name: 'Jumeau à pot-au-feu', value: 45 },
          { name: 'Onglet', value: 85 },
          { name: 'Plat de tranche', value: 25 },
          { name: 'Araignée', value: 15 },
          { name: 'Gîte à la noix', value: 55 },
          { name: "Bavette d'aloyau", value: 25 },
          { name: 'Tende de tranche', value: 65 },
          { name: 'Rond de gîte', value: 45 },
          { name: 'Bavettede de flanchet', value: 85 },
          { name: 'Flanchet', value: 35 },
          { name: 'Hampe', value: 75 },
          { name: 'Plat de côtes', value: 65 },
          { name: 'Tendron Milieu de poitrine', value: 65 },
          { name: 'Macreuse à pot-au-feu', value: 85 },
          { name: 'Rumsteck', value: 75 },
          { name: 'Faux-filet', value: 65 },
          { name: 'Côtes Entrecôtes', value: 55 },
          { name: 'Basses côtes', value: 45 },
          { name: 'Collier', value: 85 },
          { name: 'Jumeau à biftek', value: 15 },
          { name: 'Paleron', value: 65 },
          { name: 'Macreuse à bifteck', value: 45 },
          { name: 'Gîte', value: 85 },
          { name: 'Aiguillette baronne', value: 65 },
          { name: 'Filet', value: 95 }
        ]
      }
    ]
  };
  myChart.setOption(option);
});
```
