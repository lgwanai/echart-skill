# ECharts Template Mapping Index

> **请求 → 模板映射决策表。**
> - 🟢 **模板存在** → 模板模式（最快）：只需生成 data JSON
> - 🔵 **多图组合** → 组合模式：多个模板拼装到单页
> - 🟡 **无匹配模板** → 知识库兜底：读 knowledge/ + examples/ main.js 生成完整 option

---

## 🔀 映射流程（每次生成图表必须执行）

```
用户请求
    │
    ▼
Step A: 提取图表类型关键词
    bar/柱状图/柱形图 → bar/
    line/折线图/趋势图 → line/  (area/面积 → line/ + areaStyle)
    pie/饼图/占比 → pie/
    scatter/散点图/分布 → scatter/
    candlestick/K线 → candlestick/
    radar/雷达 → radar/
    gauge/仪表盘/仪表 → gauge/
    funnel/漏斗 → funnel/
    sankey/桑基 → sankey/
    treemap/树图/矩形树 → treemap/
    sunburst/旭日 → sunburst/
    graph/关系图/网络图/力导向 → graph/
    tree/树状图/组织架构 → tree/
    heatmap/热力图 → heatmap/
    map/地图 → map/
    飞线/航线/迁徙 → geo/ 或 lines/
    boxplot/箱线 → boxplot/
    parallel/平行坐标 → parallel/
    calendar/日历 → calendar/
    themeRiver/河流图 → themeRiver/
    象形/ pictorial → pictorialBar/
    chord/和弦 → chord/
    3D/三维 → 3d/
    混合/组合 → mix/
    自定义 → custom/
    │
    ▼
Step B: 提取特征关键词，选中精确模板
    bar + "堆叠" → bar/stack.html
    bar + "横向" → bar/horizontal.html
    bar + "瀑布" → bar/waterfall.html
    bar + "动态/排序/竞赛" → bar/race.html
    bar + (其他) → bar/basic.html
    line + "平滑" → line/basic.html (smooth:true)
    line + "阶梯" → line/basic.html (step:'end')
    line + "面积" → line/basic.html (areaStyle:{})
    line + "堆叠" → line/stack.html
    line + "XY/数值轴" → line/xy.html
    line + (其他) → line/basic.html
    pie + "环形" → pie/basic.html (radius: ['40%','70%'])
    pie + "玫瑰" → pie/basic.html (roseType: 'area')
    pie + (其他) → pie/basic.html
    scatter + "气泡/大小" → scatter/bubble.html
    scatter + "地图/地理" → scatter/geo.html
    scatter + (其他) → scatter/basic.html
    │
    ▼
Step C: 读取模板 HTML 文件
    → 获取 {{占位符}} 列表 = 需要生成的 data 字段
    → 根据 data 格式从 DuckDB 查询并生成匹配的 JSON
    │
    ▼
Step D: 填充 {{占位符}} → 输出最终 HTML
```

---

## 📋 完整模板映射表

### Bar（柱状图）
| 特征关键词 | 模板文件 | Data 格式 | 占位符 |
|-----------|---------|-----------|--------|
| (默认) | `bar/basic.html` | `{categories: string[], values: number[]}` | TITLE, CATEGORIES, VALUES, ROTATE |
| 堆叠、stacked | `bar/stack.html` | `{categories: string[], series: [{name,stack,data}]}` | TITLE, CATEGORIES, SERIES |
| 横向、horizontal、条形 | `bar/horizontal.html` | `{categories: string[], values: number[]}` | TITLE, CATEGORIES, VALUES |
| 瀑布、waterfall | `bar/waterfall.html` | `{categories: string[], increase: (number|null)[], decrease: (number|null)[]}` | TITLE, CATEGORIES, INCREASE, DECREASE |
| 动态、排序、竞赛、race | `bar/race.html` | `{categories: string[], values: number[]}` | TITLE, CATEGORIES, VALUES, MAX_DISPLAY |

### Line（折线图）
| 特征关键词 | 模板文件 | Data 格式 | 占位符 |
|-----------|---------|-----------|--------|
| (默认)、平滑、阶梯、面积 | `line/basic.html` | `{categories: string[], values: number[]}` | TITLE, CATEGORIES, VALUES, SMOOTH, STEP, AREA_STYLE |
| 堆叠、 stacked area | `line/stack.html` | `{categories: string[], series: [{name,stack,data,areaStyle}]}` | TITLE, CATEGORIES, SERIES |
| XY、数值坐标轴、函数 | `line/xy.html` | `[[x, y], ...]` | TITLE, DATA, SMOOTH |

### Pie（饼图）
| 特征关键词 | 模板文件 | Data 格式 | 占位符 |
|-----------|---------|-----------|--------|
| (默认)、环形、玫瑰、doughnut、rose | `pie/basic.html` | `[{name: string, value: number}, ...]` | TITLE, DATA, RADIUS, ROSE_TYPE, LABEL_SHOW |

### Scatter（散点图）
| 特征关键词 | 模板文件 | Data 格式 | 占位符 |
|-----------|---------|-----------|--------|
| (默认) | `scatter/basic.html` | `[[x, y], ...]` | TITLE, DATA, SYMBOL_SIZE |
| 气泡、bubble、大小 | `scatter/bubble.html` | `[[x, y, sizeValue], ...]` | TITLE, DATA, VMIN, VMAX, X_NAME, Y_NAME |
| 地图、geo、地理 | `scatter/geo.html` | `{geoCoordMap: {name: [lng,lat]}, data: [{name, value}]}` | TITLE, GEO_COORD_MAP, DATA, MAP_NAME, VMIN, VMAX, SIZE_SCALE |

### 其他图表类型（每种一个模板）
| 图表类型 | 关键词 | 模板文件 | Data 格式 |
|---------|--------|---------|-----------|
| K线图 | K线、candlestick、股票 | `candlestick/basic.html` | `{dates: string[], data: [[o,c,l,h],...]}` |
| 雷达图 | 雷达、radar、多维 | `radar/basic.html` | `{indicators: [{name,max}], data: [{name,value:[]}]}` |
| 仪表盘 | 仪表、gauge、进度 | `gauge/basic.html` | `{value: number, name?: string, min?, max?}` |
| 漏斗图 | 漏斗、funnel、转化 | `funnel/basic.html` | `[{name: string, value: number}, ...]` |
| 桑基图 | 桑基、sankey、流向 | `sankey/basic.html` | `{nodes: [{name}], links: [{source,target,value}]}` |
| 矩形树图 | treemap、矩形树、层级 | `treemap/basic.html` | `[{name, value?, children?}, ...]` |
| 旭日图 | 旭日、sunburst | `sunburst/basic.html` | `[{name?, value?, children?}, ...]` |
| 关系图 | 关系图、graph、网络、力导向 | `graph/force.html` | `{nodes: [{id?,name,category?}], links: [{source,target,value?}]}` |
| 关系图(固定) | 关系图+位置、固定布局 | `graph/static.html` | `{nodes: [{name,x,y}], links: [{source,target}]}` |
| 树图 | 树图、tree、组织架构 | `tree/basic.html` | `[{name, value?, children?}]` |
| 热力图 | 热力图、heatmap、矩阵 | `heatmap/basic.html` | `{xLabels: string[], yLabels: string[], data: [[x,y,v],...]}` |
| 地图 | 地图、map、省份、区域 | `map/basic.html` | `[{name: string, value: number}, ...]` (name 对应地图区域名) |
| 飞线图 | 飞线、航线、迁徙、lines | `geo/lines.html` | `{geoCoordMap: {name: [lng,lat]}, flights: [[from,to,val?]]}` |
| 涟漪散点 | 涟漪、effectScatter | `effectScatter/basic.html` | `{geoCoordMap: {name: [lng,lat]}, data: [{name,value}]}` |
| 箱线图 | 箱线、boxplot、分布 | `boxplot/basic.html` | `dataset.source: [[v1,v2,...], ...]` (每组一个子数组) |
| 平行坐标 | 平行坐标、parallel | `parallel/basic.html` | `[[dim1, dim2, ...], ...]` + parallelAxis 定义 |
| 日历图 | 日历、calendar、日期分布 | `calendar/heatmap.html` | `[[dateStr, value], ...]` |
| 主题河流 | 河流图、themeRiver | `themeRiver/basic.html` | `[[dateStr, value, seriesName], ...]` |
| 象形柱图 | 象形、pictorial、图标 | `pictorialBar/basic.html` | `{categories: string[], values: number[]}` |
| 纯飞线(无geo) | lines、航线 | `lines/flights.html` | `{geoCoordMap: {name: [lng,lat]}, flights: [[from,to,val?]]}` |
| 和弦图 | 和弦、chord | `chord/basic.html` | `{nodes: [{name}], links: [{source,target,value}]}` |

### 3D 图表（需 echarts-gl）
| 图表类型 | 关键词 | 模板文件 | Data 格式 |
|---------|--------|---------|-----------|
| 3D柱状图 | 3D柱、bar3d | `3d/bar3d.html` | `[[x, y, z], ...]` |
| 3D散点图 | 3D散点、scatter3d | `3d/scatter3d.html` | `[[x, y, z], ...]` |
| 3D曲面 | 曲面、surface | `3d/surface.html` | `{equation: {x:{}, y:{}, z: fn}}` 或 `[[x,y,z],...]` |
| 3D地球 | 地球、globe、3D地图 | `3d/globe.html` | (纹理为主，可选 scatter overlay) |
| 3D飞线 | 3D飞线、lines3d | `3d/lines3d.html` | `{geoCoordMap: {name: [lng,lat]}, flights: [[from,to]]}` |

### 混合/自定义
| 图表类型 | 关键词 | 模板文件 | Data 格式 |
|---------|--------|---------|-----------|
| 混合图 | 混合、组合、line+bar、折柱混合 | `mix/line-bar.html` | `{categories: string[], barData: number[], lineData: number[], barName?: string, lineName?: string}`；单位或量级不同必须双 yAxis，柱状 `yAxisIndex: 0`，折线 `yAxisIndex: 1` |
| 时间轴 | timeline、时间轴、切换 | `mix/timeline.html` | `{timeline: string[], categories: string[], series: [{name,type}], options: [{series:[{data}]}]}` |
| 自定义图 | 自定义、custom、特殊 | `custom/error-bar.html` | `renderItem function + data with encode` |

---

## 📐 Data Pattern Quick Reference

| Pattern | JS 格式 | 示例 |
|---------|---------|------|
| FLAT_ARRAY | `[num, num, ...]` | `[120, 200, 150, 80]` |
| NAMED_VALUE | `[{name: str, value: num}, ...]` | `[{name: "A", value: 100}]` |
| XY_PAIRS | `[[x, y], ...]` | `[[10, 20], [30, 40]]` |
| XYZ_TRIPLES | `[[x, y, z], ...]` | `[[0, 0, 5], [0, 1, 3]]` |
| OHLC | `[[open, close, low, high], ...]` | `[[20, 34, 10, 38]]` |
| GEO_VALUE | `{geoCoordMap, data: [{name, value}]}` | 见 scatter/geo 模板 |
| HIERARCHY | `[{name, value?, children:[...]}]` | treemap/sunburst/tree |
| NODES_LINKS | `{nodes: [...], links: [...]}` | sankey/graph/chord |
| RADAR_VALUE | `[{value: [num,...], name: str}]` | `[{value:[80,90,70], name:"A"}]` |
| GAUGE_VALUE | `[{value: num, name?: str}]` | `[{value: 75}]` |
| DATASET_SOURCE | `dataset: {source: [[header],[row],...]}` | boxplot/parallel/dataset |
| CALENDAR_VALUE | `[[dateStr, value], ...]` | `[["2024-01-01", 100]]` |
| LINES_COORDS | `{geoCoordMap, flights: [[from,to,val?]]}` | geo/lines/flights |
| TIMELINE_OPTIONS | `{timeline, options: [{series:[{data}]}]}` | mix/timeline |
| CUSTOM_VALUE | `renderItem fn + data + encode` | custom |
| EQUATION | `{equation: {x:{}, y:{}, z: fn}}` | 3d/surface |
