# 基于 d3 的圆形包络图 / Circle Packing with d3

**Category:** `custom`
**Example dir:** `circle-packing-with-d3`
**Difficulty:** 11

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
$.when(
  $.get(ROOT_PATH + '/data/asset/data/option-view.json'),
  $.getScript(CDN_PATH + 'd3-hierarchy@2.0.0/dist/d3-hierarchy.min.js')
).done(function (res) {
  run(res[0]);
});
function run(rawData) {
  const dataWrap = prepareData(rawData);
  initChart(dataWrap.seriesData, dataWrap.maxDepth);
}
function prepareData(rawData) {
  const seriesData = [];
  let maxDepth = 0;
  function convert(source, basePath, depth) {
    if (source == null) {
      return;
    }
    if (maxDepth > 5) {
      return;
    }
    maxDepth = Math.max(depth, maxDepth);
    seriesData.push({
      id: basePath,
      value: source.$count,
      depth: depth,
      index: seriesData.length
    });
    for (var key in source) {
      if (source.hasOwnProperty(key) && !key.match(/^\$/)) {
        var path = basePath + '.' + key;
        convert(source[key], path, depth + 1);
      }
    }
  }
  convert(rawData, 'option', 0);
  return {
    seriesData: seriesData,
    maxDepth: maxDepth
  };
}
function initChart(seriesData, maxDepth) {
  var displayRoot = stratify();
  function stratify() {
    return d3
      .stratify()
      .parentId(function (d) {
        return d.id.substring(0, d.id.lastIndexOf('.'));
      })(seriesData)
      .sum(function (d) {
        return d.value || 0;
      })
      .sort(function (a, b) {
        return b.value - a.value;
      });
  }
  function overallLayout(params, api) {
    var context = params.context;
    d3
      .pack()
      .size([api.getWidth() - 2, api.getHeight() - 2])
      .padding(3)(displayRoot);
    context.nodes = {};
    displayRoot.descendants().forEach(function (node, index) {
      context.nodes[node.id] = node;
    });
  }
  function renderItem(params, api) {
    var context = params.context;
    // Only do that layout once in each time `setOption` called.
    if (!context.layout) {
      context.layout = true;
      overallLayout(params, api);
    }
    var nodePath = api.value('id');
    var node = context.nodes[nodePath];
    if (!node) {
      // Reder nothing.
      return;
    }
    var isLeaf = !node.children || !node.children.length;
    var focus = new Uint32Array(
      node.descendants().map(function (node) {
        return node.data.index;
      })
    );
    var nodeName = isLeaf
      ? nodePath
          .slice(nodePath.lastIndexOf('.') + 1)
          .split(/(?=[A-Z][^A-Z])/g)
          .join('\n')
      : '';
    var z2 = api.value('depth') * 2;
    return {
      type: 'circle',
      focus: focus,
      shape: {
        cx: node.x,
        cy: node.y,
        r: node.r
      },
      transition: ['shape'],
      z2: z2,
      textContent: {
        type: 'text',
        style: {
          // transition: isLeaf ? 'fontSize' : null,
          text: nodeName,
          fontFamily: 'Arial',
          width: node.r * 1.3,
          overflow: 'truncate',
          fontSize: node.r / 3
        },
        emphasis: {
          style: {
            overflow: null,
            fontSize: Math.max(node.r / 
```

## Relevant Debug Patterns
## #32
 — Error Bar 空白：custom renderItem 函数无法通过占位符传递
- **日期**：2026-06-13
- **现象**：39_Custom_Error_Bar 空白
- **根因**：(1) `RENDER_ITEM: "false"` → 无渲染函数，custom 类型不知道该画什么；(2) 多行 JS 函数无法通过 Python 字符串占位符传递（换行导致语法错误）
- **修复**：(1) `renderItem` 直接硬编码在模板中；(2) 模板简化为只需 `DATA` 占位符；(3) 误差线红色 `#e54035`，柱体蓝色 `#5470c6`

---
...

## Key Points
- This is an official ECharts example from `circle-packing-with-d3/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
