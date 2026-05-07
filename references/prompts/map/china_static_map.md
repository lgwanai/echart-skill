## 图表类型：中国地图 (China Map)

**生成指令**：你现在的任务是生成一个 ECharts 的 `option` 配置。请根据以下骨架代码和数据结构要求，结合用户的实际数据进行填充和修改，生成一份完整的图表配置参数。

### ⚠️ CRITICAL: Local Static Map Usage

**DO NOT** use `$.get()` or `echarts.registerMap()` for China map!

The chart generator auto-injects `china.js` from local assets when it detects `"map": "china"` in the config. You only need to specify the map name in the series config.

**✅ CORRECT Usage**:
```json
{
  "series": [{
    "type": "map",
    "map": "china",  // Just set map name, NO $.get, NO registerMap
    "roam": true,
    "data": [{"name": "北京", "value": 15000}]
  }]
}
```

**❌ WRONG Usage (DO NOT USE)**:
```javascript
// DO NOT use $.get for local static maps
$.get(ROOT_PATH + '/data/asset/geo/china.json', function(geoJSON) {
  echarts.registerMap('china', geoJSON);  // Unnecessary!
});
```

### 数据结构要求

用户数据应包含：
- **区域名称列**：中国省份名称（中文），如"北京"、"上海"、"广东"、"浙江"等
- **数值列**：对应区域的数值，如销售额、人口、GDP等

示例数据：
```sql
SELECT 
    province,
    sales_amount
FROM sales_data
```

结果示例：
```
province    | sales_amount
------------|-------------
北京        | 15000
上海        | 12000
广东        | 18000
浙江        | 10000
江苏        | 11000
山东        | 9000
河南        | 8000
四川        | 7000
湖北        | 6000
湖南        | 5000
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
    formatter: '{b}<br/>销售额: {c}万元'  // 自定义提示格式
  },
  visualMap: {
    min: {min_value},  // 替换为数据最小值
    max: {max_value},  // 替换为数据最大值
    left: 'left',
    top: 'bottom',
    text: ['高', '低'],
    calculable: true,
    inRange: {
      color: ['#f7fbff', '#08306b']  // 渐变色
    }
  },
  series: [{
    name: '{series_name}',  // 替换为系列名称
    type: 'map',
    map: 'china',  // 关键：使用本地静态 china.js
    roam: true,
    label: {
      show: true  // 显示省份名称
    },
    emphasis: {
      label: {
        show: true,
        fontSize: 14
      }
    },
    data: [
      // 从 SQL 查询结果映射为 [{name: province, value: sales_amount}] 格式
      {name: '北京', value: 15000},
      {name: '上海', value: 12000},
      {name: '广东', value: 18000}
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
    name: row.province,
    value: row.sales_amount
  };
});
```

### 省份名称对照表

确保使用正确的中文省份名称：

| 简称 | 全称（建议使用） |
|------|------------------|
| 北京 | 北京市 或 北京 |
| 上海 | 上海市 或 上海 |
| 天津 | 天津市 或 天津 |
| 重庆 | 重庆市 或 重庆 |
| 河北 | 河北省 或 河北 |
| 山西 | 山西省 或 山西 |
| 辽宁 | 辽宁省 或 辽宁 |
| 吉林 | 吉林省 或 吉林 |
| 黑龙江 | 黑龙江省 或 黑龙江 |
| 江苏 | 江苏省 或 江苏 |
| 浙江 | 浙江省 或 浙江 |
| 安徽 | 安徽省 或 安徽 |
| 福建 | 福建省 或 福建 |
| 江西 | 江西省 或 江西 |
| 山东 | 山东省 或 山东 |
| 河南 | 河南省 或 河南 |
| 湖北 | 湖北省 或 湖北 |
| 湖南 | 湖南省 或 湖南 |
| 广东 | 广东省 或 广东 |
| 广西 | 广西壮族自治区 或 广西 |
| 海南 | 海南省 或 海南 |
| 四川 | 四川省 或 四川 |
| 贵州 | 贵州省 或 贵州 |
| 云南 | 云南省 或 云南 |
| 西藏 | 西藏自治区 或 西藏 |
| 陕西 | 陕西省 或 陕西 |
| 甘肃 | 甘肃省 或 甘肃 |
| 青海 | 青海省 或 青海 |
| 宁夏 | 宁夏回族自治区 或 宁夏 |
| 新疆 | 新疆维吾尔自治区 或 新疆 |
| 内蒙古 | 内蒙古自治区 或 内蒙古 |
| 香港 | 香港 |
| 澳门 | 澳门 |
| 台湾 | 台湾省 或 台湾 |

### 完整配置示例

```json
{
  "db_path": "workspace.duckdb",
  "query": "SELECT province, SUM(amount) as sales_amount FROM sales GROUP BY province",
  "title": "中国各省销售额分布",
  "output_path": "outputs/html/china_sales_map.html",
  "echarts_option": {
    "title": {
      "text": "中国各省销售额分布",
      "left": "center"
    },
    "tooltip": {
      "trigger": "item",
      "formatter": "{b}<br/>销售额: {c}万元"
    },
    "visualMap": {
      "min": 0,
      "max": 20000,
      "left": "left",
      "top": "bottom",
      "text": ["高", "低"],
      "calculable": true,
      "inRange": {
        "color": ["#f7fbff", "#08306b"]
      }
    },
    "series": [{
      "name": "销售额",
      "type": "map",
      "map": "china",
      "roam": true,
      "label": {
        "show": true
      },
      "data": []
    }]
  },
  "custom_js": "option.series[0].data = rawData.map(function(row) { return {name: row.province, value: row.sales_amount}; });"
}
```

### 🗺️ Map Fallback Rule

如果用户需要展示的维度在本地 `china.js` 中没有找到（例如：城市级别数据、街道数据），则**必须**使用 ECharts 百度地图扩展模式（即 `bmap` 模式）：

- **做法**：移除 `geo` 配置，改为使用 `bmap: { center: [lng, lat], zoom: 5, roam: true }`
- **系列配置**：所有的 scatter 系列必须指定 `coordinateSystem: 'bmap'`
- **依赖**：此模式需要 `BAIDU_AK` 环境变量

### 测试验证

运行测试验证地图生成：

```bash
python -m pytest tests/test_map_charts.py::TestMapChartTemplates::test_china_static_map -v
```