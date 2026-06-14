# mix-zoom-on-value

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=mix-zoom-on-value
**Chart Type:** `shadow`

## User Data Requirements

Columns needed: check data arrays in reference code for required format

## Data Arrays — Replacement Guide

The code contains **1 data array(s)** to replace:

### data[0]: `legend`
- **Format**: `[n1,n2,...] — flat value array`
- **Location**: `data: ['Growth', 'Budget 2011', 'Budget 2012']`
- **Replace with**: real data from DuckDB in the same format


## External Data Format

This example uses external data. Format from `obama_budget_proposal_2012.list.json`:

```json
{
  "budget2012List": [
    0,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    2000,
    2000,
    2000,
    2000,
    2000,
    2000,
    2000,
    2000,
    2000,
    2000,
    2000,
    2000,
    3000,
    3000,
    3000,
    3000,
    3000,
    3000,
    3000,
    4000,
    4000,
    4000,
    4000,
    5000,
    5000,
    5000,
    5000,
    6000,
    6000,
    6000,
    6000,
    6000,
    7000,
    7000,
    7000,
    8000,
    8000,
...
```

Agent: build DuckDB query to produce matching data structure.
## Agent Workflow

1. **Analyze** user table → identify columns matching the required format above
2. **Query DuckDB** → transform to match each data array's format
3. **Replace**: use **bracket-counting** to find each `data: [...]` → replace with real data
4. **Wrap HTML**: ECharts inline + div#main + script + validate_chart.py

## Reference Code

```javascript
/*
title: Mix Zoom On Value
category: bar
titleCN: 多数值轴轴缩放
difficulty: 4
*/
myChart.showLoading();
$.get(
  ROOT_PATH + '/data/asset/data/obama_budget_proposal_2012.list.json',
  function (obama_budget_2012) {
    myChart.hideLoading();
    option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
          label: {
            show: true
          }
        }
      },
      toolbox: {
        show: true,
        feature: {
          mark: { show: true },
          dataView: { show: true, readOnly: false },
          magicType: { show: true, type: ['line', 'bar'] },
          restore: { show: true },
          saveAsImage: { show: true }
        }
      },
      calculable: true,
      legend: {
        data: ['Growth', 'Budget 2011', 'Budget 2012'],
        itemGap: 5
      },
      grid: {
        top: '12%',
        left: '1%',
        right: '10%',
        containLabel: true
      },
      xAxis: [
        {
          type: 'category',
          data: obama_budget_2012.names
        }
      ],
      yAxis: [
        {
          type: 'value',
          name: 'Budget (million USD)',
          axisLabel: {
            formatter: function (a) {
              a = +a;
              return isFinite(a) ? echarts.format.addCommas(+a / 1000) : '';
            }
          }
        }
      ],
      dataZoom: [
        {
          show: true,
          start: 94,
          end: 100
        },
        {
          type: 'inside',
          start: 94,
          end: 100
        },
        {
          show: true,
          yAxisIndex: 0,
          filterMode: 'empty',
          width: 30,
          height: '80%',
          showDataShadow: false,
          left: '93%'
        }
      ],
      series: [
        {
          name: 'Budget 2011',
          type: 'bar',
          data: obama_budget_2012.budget2011List
        },
        {
          name: 'Budget 2012',
          type: 'bar',
          data: obama_budget_2012.budget2012List
        }
      ]
    };
    myChart.setOption(option);
  }
);
```
