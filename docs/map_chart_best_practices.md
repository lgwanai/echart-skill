# Map Chart Generation Best Practices

This guide provides best practices for generating map charts using local static map files.

## Core Principles

### 1. **ALWAYS Use Local Static Maps When Available**

ECharts skill provides local static map JavaScript files for common regions:
- `china.js` - China map (provinces)
- `world.js` - World map (countries)
- Province maps: `anhui.js`, `beijing.js`, `guangdong.js`, etc. (see `assets/echarts/`)

**DO NOT** use dynamic GeoJSON loading with `$.get()` and `echarts.registerMap()` for these maps!

### 2. **Correct Usage - Local Static Maps**

```javascript
// ✅ CORRECT - Use map name directly
{
  "series": [{
    "type": "map",
    "map": "china",  // Directly use map name, NO need to register
    "roam": true,
    "data": [
      {"name": "北京", "value": 15000},
      {"name": "上海", "value": 12000}
    ]
  }]
}
```

The chart generator will automatically inject the corresponding JS file:
```html
<script src="{base_url}/assets/echarts/china.js"></script>
```

### 3. **Incorrect Usage - Dynamic GeoJSON Loading**

```javascript
// ❌ WRONG - Do NOT use $.get for local static maps
$.get(ROOT_PATH + '/data/asset/geo/china.json', function (geoJSON) {
  echarts.registerMap('china', geoJSON);  // Unnecessary!
  // ...
});
```

## Map Type Decision Tree

```
User wants to visualize geographical data
         │
         ├── Is it China provinces?
         │   └── YES → Use "map": "china"
         │
         ├── Is it World countries?
         │   └── YES → Use "map": "world"
         │
         ├── Is it a Chinese province (e.g., Guangdong cities)?
         │   └── YES → Use "map": "guangdong" (or other province name)
         │
         ├── Is it city-level data WITHOUT province map?
         │   └── YES → Use bmap mode (Baidu Map API)
         │
         └── Is it other countries/regions?
             └── Check if local map JS exists
                 ├── YES → Use "map": "{name}"
                 └── NO → Use bmap mode or provide GeoJSON URL
```

## Examples

### China Map (Provinces)

```json
{
  "title": {"text": "中国各省销售额"},
  "tooltip": {"trigger": "item"},
  "visualMap": {
    "min": 0,
    "max": 100000,
    "left": "left",
    "top": "bottom",
    "text": ["高", "低"],
    "calculable": true
  },
  "series": [{
    "name": "销售额",
    "type": "map",
    "map": "china",
    "roam": true,
    "label": {"show": true},
    "data": [
      {"name": "北京", "value": 15000},
      {"name": "上海", "value": 12000}
    ]
  }]
}
```

### World Map (Countries)

```json
{
  "title": {"text": "全球销售额分布"},
  "tooltip": {"trigger": "item"},
  "visualMap": {
    "min": 0,
    "max": 1000000,
    "calculable": true
  },
  "series": [{
    "name": "销售额",
    "type": "map",
    "map": "world",
    "roam": true,
    "data": [
      {"name": "China", "value": 500000},
      {"name": "United States", "value": 450000}
    ]
  }]
}
```

### Province Map (Cities)

```json
{
  "title": {"text": "广东省各城市人口"},
  "tooltip": {"trigger": "item"},
  "visualMap": {"min": 0, "max": 20000000},
  "series": [{
    "name": "人口",
    "type": "map",
    "map": "guangdong",
    "roam": true,
    "label": {"show": true},
    "data": [
      {"name": "广州市", "value": 15000000},
      {"name": "深圳市", "value": 13000000}
    ]
  }]
}
```

### BMap Mode (City-level or Street-level)

When you need city-level or street-level data that's not covered by local static maps:

```json
{
  "bmap": {
    "center": [113.23, 23.16],
    "zoom": 10,
    "roam": true
  },
  "series": [{
    "name": "门店",
    "type": "scatter",
    "coordinateSystem": "bmap",
    "data": [
      {"name": "天河店", "value": [113.33, 23.12, 1000]},
      {"name": "越秀店", "value": [113.26, 23.13, 800]}
    ]
  }]
}
```

**Note**: BMap mode requires `BAIDU_AK` environment variable.

### Geo Coordinate System (Scatter on Map)

Use `geo` component + `scatter` series for custom point locations:

```json
{
  "geo": {
    "map": "china",
    "roam": true,
    "label": {"show": true}
  },
  "series": [{
    "name": "销售点",
    "type": "scatter",
    "coordinateSystem": "geo",
    "data": [
      {"name": "北京", "value": [116.46, 39.92, 15000]},
      {"name": "上海", "value": [121.48, 31.22, 12000]}
    ],
    "symbolSize": 20
  }]
}
```

## Common Pitfalls

### ❌ Pitfall 1: Using $.get for Local Static Maps

```javascript
// WRONG
$.get(ROOT_PATH + '/data/asset/geo/china.json', function (geoJSON) {
  echarts.registerMap('china', geoJSON);
  option = {
    series: [{"type": "map", "map": "china", "data": data}]
  };
  myChart.setOption(option);
});
```

**Problem**: The external GeoJSON file doesn't exist in the deployment environment.

**Solution**: Use `"map": "china"` directly without $.get.

### ❌ Pitfall 2: Pie Charts on Geo Map

```javascript
// WRONG - pie series doesn't support coordinateSystem: 'geo'
{
  "series": [{
    "type": "pie",
    "coordinateSystem": "geo",  // NOT SUPPORTED!
    "center": [116.46, 39.92],
    "data": [...]
  }]
}
```

**Problem**: ECharts `pie` series doesn't support `coordinateSystem: 'geo'`.

**Solution**: Use `scatter` or `effectScatter` with bubble sizes to represent values.

### ❌ Pitfall 3: Missing Province Map JS

```json
{
  "series": [{
    "map": "guangdong"  // Requires guangdong.js
  }]
}
```

**Problem**: If `guangdong.js` is not injected, the map won't render.

**Solution**: The chart generator automatically detects province names and injects the correct JS file. Just ensure the province name matches the file name (e.g., "guangdong", "beijing").

## Data Mapping

### Province Names (China)

Use Chinese names for province data:
- 北京
- 上海 (Shanghai)
- 广东
- 浙江
- 江苏
- etc.

### Country Names (World)

Use English names for world map:
- China
- United States
- Japan
- Germany
- United Kingdom
- etc.

### City Names (Province Maps)

Use full Chinese city names:
- 广州市
- 深圳市
- 东莞市
- etc.

## Testing

Always test map charts with the test suite:

```bash
python -m pytest tests/test_map_charts.py -v
```

This validates:
- Local static map JS files are correctly injected
- No remote CDN links are used
- No dynamic $.get() for GeoJSON loading
- Correct map types and configurations

## Summary

| Map Type | Use | No Need | Auto-injected JS |
|----------|-----|---------|------------------|
| China provinces | `"map": "china"` | `$.get` + `registerMap` | `china.js` |
| World countries | `"map": "world"` | `$.get` + `registerMap` | `world.js` |
| Chinese provinces | `"map": "guangdong"` | `$.get` + `registerMap` | `guangdong.js` |
| City-level | `"bmap": {...}` | Local static map | `bmap.min.js` + Baidu API |
| Custom regions | GeoJSON URL | Local static | User-provided |

**Golden Rule**: Always prefer local static maps (china.js, world.js, provinces) over dynamic GeoJSON loading.