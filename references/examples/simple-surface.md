# Simple Surface / Simple Surface

**Category:** `surface`
**Example dir:** `simple-surface`
**Difficulty:** 

## Template Match
- **3d/surface.html** — Surface

## Option Code
```javascript
option = {
  tooltip: {},
  backgroundColor: '#fff',
  visualMap: {
    show: false,
    dimension: 2,
    min: -1,
    max: 1,
    inRange: {
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
      ]
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
    viewControl: {
      // projection: 'orthographic'
    }
  },
  series: [
    {
      type: 'surface',
      wireframe: {
        // show: false
      },
      equation: {
        x: {
          step: 0.05
        },
        y: {
          step: 0.05
        },
        z: function (x, y) {
          if (Math.abs(x) < 0.1 && Math.abs(y) < 0.1) {
            return '-';
          }
          return Math.sin(x * Math.PI) * Math.sin(y * Math.PI);
        }
      }
    }
  ]
};
```

## Relevant Debug Patterns
## #28
 — 3D Scatter/Surface/Globe/Lines3D 同样空白
- **日期**：2026-06-13
- **现象**：34/35/36/37 全部空白
- **根因**：与 #27 相同——GL_INLINE 破坏注入 + 模板配置偏离官方示例。所有 3D 模板统一修复
- **修复**：3d/scatter3d.html、3d/surface.html、3d/globe.html、3d/lines3d.html 全部改为与官方示例一致的配置。关键：`zAxis3D: {}`（非 `{type:'value'}`）、`grid3D: {}`、无 `coordinateSystem`

---
...

## #29
 — Surface 空白：JS 函数被 `_json_safe` 加引号变成字符串
- **日期**：2026-06-13
- **现象**：35_3D_Surface 空白，JS 函数 `function(x,y){...}` 被当成字符串输出 `'function(x,y){...}'`
- **根因**：`build_template.py` 的 `_json_safe` 不支持函数字符串，所有字符串值都被包在引号中
- **修复**：(1) `_json_safe` 新增检测：以 `function` 或 `(` 开头的字符串直接原样返回；(2) surface 模板改为与官方示例一致的 `equation: {x,y,z}` 结构

---
...

## Key Points
- This is an official ECharts example from `simple-surface/main.js`
- Template data format: `equation.z as JS function`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
