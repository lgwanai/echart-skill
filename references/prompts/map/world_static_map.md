## 图表类型：世界地图 (World Map)

**生成指令**：你现在的任务是生成一个 ECharts 的 `option` 配置。请根据以下骨架代码和数据结构要求，结合用户的实际数据进行填充和修改，生成一份完整的图表配置参数。

### ⚠️ CRITICAL: Local Static Map Usage

**DO NOT** use `$.get()` or `echarts.registerMap()` for World map!

The chart generator auto-injects `world.js` from local assets when it detects `"map": "world"` in the config. You only need to specify the map name in the series config.

**✅ CORRECT Usage**:
```json
{
  "series": [{
    "type": "map",
    "map": "world",  // Just set map name, NO $.get, NO registerMap
    "roam": true,
    "data": [{"name": "China", "value": 500000}]
  }]
}
```

**❌ WRONG Usage (DO NOT USE)**:
```javascript
// DO NOT use $.get for local static maps
$.get(ROOT_PATH + '/data/asset/geo/world.json', function(geoJSON) {
  echarts.registerMap('world', geoJSON);  // Unnecessary!
});
```

### 数据结构要求

用户数据应包含：
- **国家名称列**：国家名称（英文），如"China"、"United States"、"Japan"等
- **数值列**：对应国家的数值，如销售额、GDP、人口等

示例数据：
```sql
SELECT 
    country,
    revenue
FROM global_sales
```

结果示例：
```
country        | revenue
---------------|--------
China          | 500000
United States  | 450000
Japan          | 300000
Germany        | 250000
United Kingdom | 200000
```

### ECharts Option 骨架参考

```javascript
option = {
  title: {
    text: '{title}',  // 替换为用户的图表标题
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{b}<br/>营收: {c}万美元'  // 自定义提示格式
  },
  visualMap: {
    min: {min_value},  // 替换为数据最小值
    max: {max_value},  // 替换为数据最大值
    left: 'left',
    top: 'bottom',
    text: ['High', 'Low'],
    calculable: true,
    inRange: {
      color: ['#ffffbf', '#8c510a']  // 渐变色
    }
  },
  series: [{
    name: '{series_name}',  // 替换为系列名称
    type: 'map',
    map: 'world',  // 关键：使用本地静态 world.js
    roam: true,
    label: {
      show: false  // 世界地图通常不显示所有国家名称
    },
    emphasis: {
      label: {
        show: true  // 高亮时显示国家名称
      }
    },
    data: [
      // 从 SQL 查询结果映射为 [{name: country, value: revenue}] 格式
      {name: 'China', value: 500000},
      {name: 'United States', value: 450000},
      {name: 'Japan', value: 300000}
    ]
  }]
};
```

### custom_js 数据映射

在 `custom_js` 中，将 SQL 查询结果映射到地图数据：

```javascript
// 将 rawData (SQL 查询结果) 映射到 series.data
option.series[0].data = rawData.map(function(row) {
  return {
    name: row.country,
    value: row.revenue
  };
});
```

### 国家名称对照表

确保使用正确的英文国家名称（与 `world.js` 中的名称匹配）：

| 中文名称 | 英文名称（world.js） |
|----------|----------------------|
| 中国 | China |
| 美国 | United States 或 United States of America |
| 日本 | Japan |
| 德国 | Germany |
| 英国 | United Kingdom |
| 法国 | France |
| 意大利 | Italy |
| 俄罗斯 | Russia |
| 印度 | India |
| 巴西 | Brazil |
| 澳大利亚 | Australia |
| 加拿大 | Canada |
| 韩国 | South Korea 或 Korea |
| 墨西哥 | Mexico |
| 西班牙 | Spain |
| 印度尼西亚 | Indonesia |
| 泰国 | Thailand |
| 越南 | Vietnam |
| 菲律宾 | Philippines |
| 马来西亚 | Malaysia |
| 新加坡 | Singapore |
| 新西兰 | New Zealand |
| 南非 | South Africa |
| 埃及 | Egypt |
| 尼日利亚 | Nigeria |
| 阿根廷 | Argentina |
| 智利 | Chile |
| 哥伦比亚 | Colombia |
| 挪威 | Norway |
| 瑞典 | Sweden |
| 丹麦 | Denmark |
| 芬兰 | Finland |
| 瑞士 | Switzerland |
| 荷兰 | Netherlands |
| 比利时 | Belgium |
| 奥地利 | Austria |
| 葡萄牙 | Portugal |
| 波兰 | Poland |
| 土耳其 | Turkey |
| 乌克兰 | Ukraine |
| 沙特阿拉伯 | Saudi Arabia |
| 以色列 | Israel |
| 阿联酋 | United Arab Emirates |
| 伊朗 | Iran |
| 巴基斯坦 | Pakistan |
| 孟加拉国 | Bangladesh |

### 完整配置示例

```json
{
  "db_path": "workspace.duckdb",
  "query": "SELECT country, SUM(revenue) as total_revenue FROM global_sales GROUP BY country",
  "title": "全球各国营收分布",
  "output_path": "outputs/html/world_revenue_map.html",
  "echarts_option": {
    "title": {
      "text": "全球各国营收分布",
      "left": "center"
    },
    "tooltip": {
      "trigger": "item",
      "formatter": "{b}<br/>营收: {c}万美元"
    },
    "visualMap": {
      "min": 0,
      "max": 600000,
      "left": "left",
      "top": "bottom",
      "text": ["High", "Low"],
      "calculable": true,
      "inRange": {
        "color": ["#ffffbf", "#8c510a"]
      }
    },
    "series": [{
      "name": "营收",
      "type": "map",
      "map": "world",
      "roam": true,
      "label": {
        "show": false
      },
      "emphasis": {
        "label": {
          "show": true
        }
      },
      "data": []
    }]
  },
  "custom_js": "option.series[0].data = rawData.map(function(row) { return {name: row.country, value: row.total_revenue}; });"
}
```

### 🗺️ Map Fallback Rule

如果用户需要展示的维度在本地 `world.js` 中没有找到足够详细的数据（例如：特定国家的州/省级别、城市级别），则**必须**使用 ECharts 百度地图扩展模式（即 `bmap` 模式）或其他地图服务：

- **做法**：移除 `geo` 配置，改为使用 `bmap: { center: [lng, lat], zoom: 5, roam: true }`
- **系列配置**：所有的 scatter 系列必须指定 `coordinateSystem: 'bmap'`
- **依赖**：此模式需要 `BAIDU_AK` 环境变量

### 测试验证

运行测试验证地图生成：

```bash
python -m pytest tests/test_map_charts.py::TestMapChartTemplates::test_world_static_map -v
```