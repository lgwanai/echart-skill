# sankey-simple

**Official:** https://echarts.apache.org/examples/zh/editor.html?c=sankey-simple

## ⚠️ TWO data arrays must be replaced
- `series.data` = **nodes**: `[{name: "a"}, {name: "b"}, ...]`
- `series.links` = **links**: `[{source: "a", target: "a1", value: 5}, ...]`
Both come from DuckDB `test_sankey_data` (src, tgt, val columns).

## Reference Code (DO NOT use as-is — replace data + links)
```javascript
option = {
  series: {
    type: 'sankey',
    layout: 'none',
    emphasis: { focus: 'adjacency' },
    data: [{name:'a'},{name:'b'},{name:'a1'},{name:'a2'},{name:'b1'},{name:'c'}],
    links: [{source:'a',target:'a1',value:5},{source:'a',target:'a2',value:3},{source:'b',target:'b1',value:8},{source:'a',target:'b1',value:3},{source:'b1',target:'a1',value:1},{source:'b1',target:'c',value:2}]
  }
};
```

## Agent Workflow
1. Query DuckDB: `SELECT src, tgt, val FROM test_sankey_data`
2. Extract unique node names → `[{name}, ...]`
3. Build links → `[{source, target, value}, ...]`
4. Replace BOTH `data:` AND `links:` arrays in option
5. Wrap in HTML → validate
