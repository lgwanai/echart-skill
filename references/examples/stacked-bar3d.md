# stacked-bar3d

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=stacked-bar3d
**Chart Type:** `bar3D`

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
title: Stacked Bar3D
category: bar3D
titleCN: ä¸ç»´å å æ±ç¶å¾
*/
$.getScript(CDN_PATH + 'simplex-noise@2.4.0/simplex-noise.js').done(
  function () {
    function generateData() {
      var data = [];
      var noise = new SimplexNoise(Math.random);
      for (var i = 0; i <= 10; i++) {
        for (var j = 0; j <= 10; j++) {
          var value = noise.noise2D(i / 5, j / 5);
          data.push([i, j, value * 2 + 4]);
        }
      }
      return data;
    }
    var series = [];
    for (var i = 0; i < 10; i++) {
      series.push({
        type: 'bar3D',
        data: generateData(),
        stack: 'stack',
        shading: 'lambert',
        emphasis: {
          label: {
            show: false
          }
        }
      });
    }
    myChart.setOption({
      xAxis3D: {
        type: 'value'
      },
      yAxis3D: {
        type: 'value'
      },
      zAxis3D: {
        type: 'value'
      },
      grid3D: {
        viewControl: {
          // autoRotate: true
        },
        light: {
          main: {
            shadow: true,
            quality: 'ultra',
            intensity: 1.5
          }
        }
      },
      series: series
    });
  }
);
```
