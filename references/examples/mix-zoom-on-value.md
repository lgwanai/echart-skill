# mix-zoom-on-value

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=mix-zoom-on-value
**Chart Type:** `shadow`

## IMPORTANT

Code below shows OFFICIAL DISPLAY DATA. Agent MUST replace all `data: [...]` arrays with the user's real DuckDB data using **bracket-counting** (not simple regex).

## Agent Workflow

1. **Analyze user data**: check data arrays in reference code
2. **Query DuckDB**: Build SQL against the user's actual table and columns
3. **Transform**: Map query results to match the data array format below
4. **Replace data**: Find `data: [` → count brackets [ ] to find complete array → replace with real JSON
5. **Wrap HTML**: ECharts script inline + div#main + init + setOption + resize
6. **Validate**: `python scripts/validate_chart.py output.html`

Data arrays to replace: **1**

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
