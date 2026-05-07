# Map Chart Generation Best Practices

This guide provides best practices for generating map charts using local static map files.

## Map Hierarchy and Usage Rules

### 🎯 **Three-Level Map Hierarchy**

| Level | Coverage | Data Source | Usage |
|-------|----------|-------------|-------|
| **Province Level** | China provinces (北京, 上海, 广东...) | `china.js` | ✅ Always use local static map |
| **City Level** | Cities within a province (广州, 深圳, 东莞...) | Province JS (e.g., `guangdong.js`) | ✅ Use local static province map |
| **District/Street Level** | Districts, streets, custom locations | Baidu Map API | ⚠️ Requires `BAIDU_AK` |

### 🎯 **Core Principles**

### 1. **ALWAYS Use Local Static Maps When Available**

ECharts skill provides local static map JavaScript files:
- **National**: `china.js` (contains all provinces)
- **Global**: `world.js` (contains all countries)
- **Provincial**: `guangdong.js`, `beijing.js`, `zhejiang.js`, etc. (each contains all cities in that province)

**Example**: Guangdong province map (`guangdong.js`) includes:
- 广州市 (Guangzhou)
- 深圳市 (Shenzhen)
- 东莞市 (Dongguan)
- 中山市 (Zhongshan)
- 佛山市 (Foshan)
- etc. (21 cities total)

**DO NOT** use dynamic GeoJSON loading with `$.get()` and `echarts.registerMap()` for these maps!

### 2. **Correct Usage - Local Static Maps**

#### **Province Level (China Provinces)**
```json
{
  "series": [{
    "type": "map",
    "map": "china",  // Use china.js
    "data": [
      {"name": "北京", "value": 15000},
      {"name": "广东", "value": 18000}
    ]
  }]
}
```

#### **City Level (Cities within a Province)**
```json
{
  "series": [{
    "type": "map",
    "map": "guangdong",  // Use guangdong.js (contains 21 cities)
    "data": [
      {"name": "广州市", "value": 5000},
      {"name": "深圳市", "value": 6000},
      {"name": "东莞市", "value": 3000}
    ]
  }]
}
```

#### **District/Street Level (Requires Baidu Map)**
```json
{
  "bmap": {
    "center": [113.26, 23.13],  // Guangzhou coordinates
    "zoom": 12,
    "roam": true
  },
  "series": [{
    "type": "scatter",
    "coordinateSystem": "bmap",
    "data": [
      {"name": "天河区", "value": [113.33, 23.12, 1000]}
    ]
  }]
}
```

**Note**: BMap mode requires `BAIDU_AK` environment variable.

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
         ├── What granularity level?
         │
         ├── 1️⃣ PROVINCE LEVEL (中国省份)
         │   ├── Beijing, Shanghai, Guangdong, Zhejiang...
         │   └── ✅ Use "map": "china" (china.js)
         │       └── Data: [{"name": "北京", "value": 15000}]
         │
         ├── 2️⃣ CITY LEVEL (省内城市)
         │   ├── Guangzhou, Shenzhen, Dongguan (in Guangdong)
         │   ├── Hangzhou, Ningbo (in Zhejiang)
         │   └── ✅ Use "map": "guangdong" (guangdong.js)
         │       └── Data: [{"name": "广州市", "value": 5000}]
         │
         └── 3️⃣ DISTRICT/STREET LEVEL (区县、街道)
             ├── Tianhe District (天河区)
             ├── Specific locations
             └── ⚠️ Use "bmap" mode (requires BAIDU_AK)
                 └── Data: [{"name": "天河区", "value": [lng, lat, val]}]
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

**Example: Guangdong Province Cities**

```json
{
  "title": {"text": "广东省各城市人口"},
  "tooltip": {"trigger": "item"},
  "visualMap": {"min": 0, "max": 20000000},
  "series": [{
    "name": "人口",
    "type": "map",
    "map": "guangdong",  // Uses guangdong.js (contains 21 cities)
    "roam": true,
    "label": {"show": true},
    "data": [
      {"name": "广州市", "value": 15000000},
      {"name": "深圳市", "value": 13000000},
      {"name": "东莞市", "value": 8000000},
      {"name": "佛山市", "value": 7000000}
    ]
  }]
}
```

**Available Province Maps** (see `assets/echarts/`):
- `anhui.js` (安徽 - 16 cities)
- `beijing.js` (北京 - districts)
- `chongqing.js` (重庆 - districts)
- `fujian.js` (福建 - 9 cities)
- `guangdong.js` (广东 - 21 cities)
- `guangxi.js` (广西 - 14 cities)
- `guizhou.js` (贵州 - 9 cities)
- `hainan.js` (海南 - 4 cities)
- `hebei.js` (河北 - 11 cities)
- `heilongjiang.js` (黑龙江 - 13 cities)
- `henan.js` (河南 - 18 cities)
- `hubei.js` (湖北 - 17 cities)
- `hunan.js` (湖南 - 14 cities)
- `jiangsu.js` (江苏 - 13 cities)
- `jiangxi.js` (江西 - 11 cities)
- `jilin.js` (吉林 - 9 cities)
- `liaoning.js` (辽宁 - 14 cities)
- `neimenggu.js` (内蒙古 - 12 cities)
- `ningxia.js` (宁夏 - 5 cities)
- `qinghai.js` (青海 - 8 cities)
- `shandong.js` (山东 - 17 cities)
- `shanghai.js` (上海 - districts)
- `shanxi.js` (山西 - 11 cities)
- `shanxi1.js` (陕西 - 10 cities)
- `sichuan.js` (四川 - 21 cities)
- `taiwan.js` (台湾)
- `tianjin.js` (天津 - districts)
- `xianggang.js` (香港)
- `xinjiang.js` (新疆 - 24 cities)
- `xizang.js` (西藏 - 7 cities)
- `yunnan.js` (云南 - 16 cities)
- `zhejiang.js` (浙江 - 11 cities)

**City Names Format**: Use full Chinese name (e.g., "广州市", "深圳市")

### BMap Mode (District/Street Level)

**When to Use BMap Mode**:
1. ✅ District/county level data (区县级别) - e.g., 天河区, 南山区
2. ✅ Street level data (街道级别)
3. ✅ Custom locations not in static maps
4. ❌ NOT for province-level data (use china.js)
5. ❌ NOT for city-level data (use province.js)

**Example**:

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