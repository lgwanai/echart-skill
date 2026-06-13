# Globe with ECharts Surface / Globe with ECharts Surface

**Category:** `globe`
**Example dir:** `globe-with-echarts-surface`
**Difficulty:** 

## Template Match
- **3d/globe.html** — Globe

## Option Code
```javascript
var canvas = document.createElement('canvas');
var mapChart = echarts.init(canvas, null, {
  width: 4096,
  height: 2048
});
mapChart.setOption({
  backgroundColor: '#fff',
  visualMap: {
    show: false,
    min: 0,
    max: 500000,
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
  series: [
    {
      type: 'map',
      map: 'world',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      boundingCoords: [
        [-180, 90],
        [180, -90]
      ],
      data: [
        { name: 'Afghanistan', value: 28397.812 },
        { name: 'Angola', value: 19549.124 },
        { name: 'Albania', value: 3150.143 },
        { name: 'United Arab Emirates', value: 8441.537 },
        { name: 'Argentina', value: 40374.224 },
        { name: 'Armenia', value: 2963.496 },
        { name: 'French Southern and Antarctic Lands', value: 268.065 },
        { name: 'Australia', value: 22404.488 },
        { name: 'Austria', value: 8401.924 },
        { name: 'Azerbaijan', value: 9094.718 },
        { name: 'Burundi', value: 9232.753 },
        { name: 'Belgium', value: 10941.288 },
        { name: 'Benin', value: 9509.798 },
        { name: 'Burkina Faso', value: 15540.284 },
        { name: 'Bangladesh', value: 151125.475 },
        { name: 'Bulgaria', value: 7389.175 },
        { name: 'The Bahamas', value: 66402.316 },
        { name: 'Bosnia and Herzegovina', value: 3845.929 },
        { name: 'Belarus', value: 9491.07 },
        { name: 'Belize', value: 308.595 },
        { name: 'Bermuda', value: 64.951 },
        { name: 'Bolivia', value: 716.939 },
        { name: 'Brazil', value: 195210.154 },
        { name: 'Brunei', value: 27.223 },
        { name: 'Bhutan', value: 716.939 },
        { name: 'Botswana', value: 1969.341 },
        { name: 'Central African Republic', value: 4349.921 },
        { name: 'Canada', value: 34126.24 },
        { name: 'Switzerland', value: 7830.534 },
        { name: 'Chile', value: 17150.76 },
        { name: 'China', value: 1359821.465 },
        { name: 'Ivory Coast', value: 60508.978 },
        { name: 'Cameroon', value: 20624.343 },
        { name: 'Democratic Republic of the Congo', value: 62191.161 },
        { name: 'Republic of the Congo', value: 3573.024 },
        { name: 'Colombia', value: 46444.798 },
        { name: 'Costa Rica', value: 4669.685 },
        { name: 'Cuba', value: 11281.768 },
        { name: 'Northern Cyprus', value: 1.468 },
        { name: 'Cyprus', value: 1103.685 },
        { name: 'Czech Republic', value: 10553.701 },
        { name: 'Germany', value: 83017.404 },
        { name: 'Djibouti', value: 834.036 },
        { name: 'Denmark', value: 5550.959 },
        { name: 'Dominican Republic', value: 10016.797 },
        { name: 'Algeria', value: 37062.82 },
        { name: 'E
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

## #30
 — Globe 无纹理显示为纯色/空白球
- **日期**：2026-06-13
- **现象**：36_3D_Globe 显示为纯蓝/黄色球，无地球纹理
- **根因**：未提供 `baseTexture`，ECharts globe 渲染为无纹理球体
- **修复**：下载 ECharts 官方示例的 1.3MB JPG 地球纹理（`echarts.apache.org/examples/data-gl/asset/world.topo.bathy.200401.jpg`），base64 嵌入为 `baseTexture`

---
...

## Key Points
- This is an official ECharts example from `globe-with-echarts-surface/main.js`
- Template data format: `[[lat, lng, value], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
