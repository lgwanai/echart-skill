# scatter-simple

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=scatter-simple

## ⚠️ Real Data REQUIRED
Replace the `data: [[x,y],...]` array in `series[0]` with real DuckDB data.
Use bracket-counting to match the COMPLETE array (not regex `[^\]]*` which truncates).

## Reference Code (REPLACE data array)
```javascript
option = {
  xAxis: {}, yAxis: {},
  series: [{
    symbolSize: 20,
    data: [[10.0,8.04],[8.07,6.95],[13.0,7.58],[9.05,8.81],[11.0,8.33],[14.0,7.66],[13.4,6.81],[10.0,6.33],[14.0,8.96],[12.5,6.82],[9.15,7.2],[11.5,7.2],[3.03,4.23],[12.2,7.83],[2.02,4.47],[1.05,3.33],[4.05,4.96],[6.03,7.24],[12.0,6.26],[12.0,8.84],[7.08,5.82],[5.02,5.68]],
    type: 'scatter'
  }]
};
```

## Agent Workflow
1. Query DuckDB: `SELECT x, y FROM test_scatter_data`
2. Build data: `[[x,y], ...]` JSON array
3. Find `data: [` in code → count brackets to find matching `]` → replace ENTIRE array
4. Wrap in HTML → validate
