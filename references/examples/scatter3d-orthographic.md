# scatter3d-orthographic

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter3d-orthographic
**Chart Type:** `value`

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
title: Scatter3D - Orthographic
category: scatter3D
theme: dark
titleCN: ä¸ç»´æ£ç¹å¾ - æ­£äº¤æå½±
*/
$.getScript(CDN_PATH + 'simplex-noise@2.4.0/simplex-noise.js').done(
  function () {
    var noise = new SimplexNoise(Math.random);
    function generateData(theta, min, max) {
      var data = [];
      for (var i = 0; i <= 40; i++) {
        for (var j = 0; j <= 40; j++) {
          for (var k = 0; k <= 40; k++) {
            var value = noise.noise3D(i / 20, j / 20, k / 20);
            valMax = Math.max(valMax, value);
            valMin = Math.min(valMin, value);
            data.push([i, j, k, value * 2 + 4]);
          }
        }
      }
      return data;
    }
    var valMin = Infinity;
    var valMax = -Infinity;
    var data = generateData(2, -5, 5);
    console.log(valMin, valMax);
    myChart.setOption(
      (option = {
        visualMap: {
          show: false,
          min: 2,
          max: 6,
          inRange: {
            symbolSize: [0.5, 15],
            color: [
              '#313695',
              '#4575b4',
              '#74add1',
              '#abd9e9',
              '#e0f3f8',
              '#ffffbf',
              '#fee090',
              '#fdae61',
              '#f46d43',
              '#d73027',
              '#a50026'
            ],
            colorAlpha: [0.2, 1]
          }
        },
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
          axisLine: {
            lineStyle: { color: '#fff' }
          },
          axisPointer: {
            lineStyle: { color: '#fff' }
          },
          viewControl: {
            projection: 'orthographic'
          }
        },
        series: [
          {
            type: 'scatter3D',
            data: data
          }
        ]
      })
    );
  }
);
```
