# 全国主要城市空气质量 / Air Quality

**Category:** `scatter`
**Example dir:** `effectScatter-map`
**Difficulty:** 2

## Template Match
- **3d/scatter3d.html** — Scatter3D

## Option Code
```javascript
const data = [
  { name: '海门', value: 9 },
  { name: '鄂尔多斯', value: 12 },
  { name: '招远', value: 12 },
  { name: '舟山', value: 12 },
  { name: '齐齐哈尔', value: 14 },
  { name: '盐城', value: 15 },
  { name: '赤峰', value: 16 },
  { name: '青岛', value: 18 },
  { name: '乳山', value: 18 },
  { name: '金昌', value: 19 },
  { name: '泉州', value: 21 },
  { name: '莱西', value: 21 },
  { name: '日照', value: 21 },
  { name: '胶南', value: 22 },
  { name: '南通', value: 23 },
  { name: '拉萨', value: 24 },
  { name: '云浮', value: 24 },
  { name: '梅州', value: 25 },
  { name: '文登', value: 25 },
  { name: '上海', value: 25 },
  { name: '攀枝花', value: 25 },
  { name: '威海', value: 25 },
  { name: '承德', value: 25 },
  { name: '厦门', value: 26 },
  { name: '汕尾', value: 26 },
  { name: '潮州', value: 26 },
  { name: '丹东', value: 27 },
  { name: '太仓', value: 27 },
  { name: '曲靖', value: 27 },
  { name: '烟台', value: 28 },
  { name: '福州', value: 29 },
  { name: '瓦房店', value: 30 },
  { name: '即墨', value: 30 },
  { name: '抚顺', value: 31 },
  { name: '玉溪', value: 31 },
  { name: '张家口', value: 31 },
  { name: '阳泉', value: 31 },
  { name: '莱州', value: 32 },
  { name: '湖州', value: 32 },
  { name: '汕头', value: 32 },
  { name: '昆山', value: 33 },
  { name: '宁波', value: 33 },
  { name: '湛江', value: 33 },
  { name: '揭阳', value: 34 },
  { name: '荣成', value: 34 },
  { name: '连云港', value: 35 },
  { name: '葫芦岛', value: 35 },
  { name: '常熟', value: 36 },
  { name: '东莞', value: 36 },
  { name: '河源', value: 36 },
  { name: '淮安', value: 36 },
  { name: '泰州', value: 36 },
  { name: '南宁', value: 37 },
  { name: '营口', value: 37 },
  { name: '惠州', value: 37 },
  { name: '江阴', value: 37 },
  { name: '蓬莱', value: 37 },
  { name: '韶关', value: 38 },
  { name: '嘉峪关', value: 38 },
  { name: '广州', value: 38 },
  { name: '延安', value: 38 },
  { name: '太原', value: 39 },
  { name: '清远', value: 39 },
  { name: '中山', value: 39 },
  { name: '昆明', value: 39 },
  { name: '寿光', value: 40 },
  { name: '盘锦', value: 40 },
  { name: '长治', value: 41 },
  { name: '深圳', value: 41 },
  { name: '珠海', value: 42 },
  { name: '宿迁', value: 43 },
  { name: '咸阳', value: 43 },
  { name: '铜川', value: 44 },
  { name: '平度', value: 44 },
  { name: '佛山', value: 44 },
  { name: '海口', value: 44 },
  { name: '江门', value: 45 },
  { name: '章丘', value: 45 },
  { name: '肇庆', value: 46 },
  { name: '大连', value: 47 },
  { name: '临汾', value: 47 },
  { name: '吴江', value: 47 },
  { name: '石嘴山', value: 49 },
  { name: '沈阳', value: 50 },
  { name: '苏州', value: 50 },
  { name: '茂名', value: 50 },
  { name: '嘉兴', value: 51 },
  { name: '长春', value: 51 },
  { name: '胶州', value: 52 },
  { name: '银川', value: 52 },
  { name: '张家港', value: 52 },
  { name: '三门峡', value: 53 },
  { name: '锦州', value: 54 },
  { name: '南昌', value: 54 },
  { name: '柳州', value: 54 },
  { name: '三亚', value: 54 },
  { name: '自贡', value: 56 },
  { name: '吉林', value: 56 },
  { name: '阳江', value: 57 },
  { name: '泸州', value: 57 },
  { name: '西宁', value: 57 },
  { name: '宜宾', value: 58 },
  { name: '呼和浩特
```

## Relevant Debug Patterns
## #18
 — Scatter Geo/Map 空白：MAP_INLINE 被替换导致地图未加载
- **日期**：2026-06-13
- **现象**：12_Scatter_Geo、13_Map_China 等地图类图表空白
- **根因**：数据 dict 中 `"MAP_INLINE": ""` → `_json_safe` 替换 `{{MAP_INLINE}}` 为 `''` → `<!-- {{MAP_INLINE}} -->` 变成 `<!-- '' -->` → `build_template.py` 的地图注入检测 `if "<!-- {{MAP_INLINE}} -->" in html` 失败 → China GeoJSON 未嵌入 → 地图空白
- **修复**：**不要在数据 dict 中提供 `MAP_INLINE`/`GL_INLINE`/`ECHARTS_INLINE` 这三个特殊占位符**。它们由 `build_template.py` 自动处理（代码中已排除此三类占位符的校验）。**模板不需要修改**——模板中的 `<!-- {{MAP_INLINE}} --...

## #19
 — Scatter Geo 气泡大小无差异
- **日期**：2026-06-13
- **现象**：12_Scatter_Geo 所有气泡一样大
- **根因**：模板 `symbolSize: function(val) { return Math.sqrt(val[2]) / SIZE_SCALE || 8; }` 中 `Math.sqrt` 压缩了数值差异。值 70-100 经 sqrt 后为 8.4-10，差值仅 1.6px，肉眼不可分辨
- **修复**：模板改为 `val[2] / {{SIZE_SCALE}}`（线性），SIZE_SCALE=5 → 14-20px 可分辨范围

---
...

## #25
 — EffectScatter 空白 + 颜色不生效
- **日期**：2026-06-13
- **现象**：30_EffectScatter 一片空白，修复后各城市同色
- **根因**：(1) `GEO_COORD_MAP: "{}"` 空对象，`MAP_NAME: ""` 空地图名 → 无地图；(2) `convertData()` 只复制 `name`/`value`，丢弃 `itemStyle`
- **修复**：(1) 提供真实 GEO_COORD_MAP + MAP_NAME="china"；(2) `convertData` 保留 `itemStyle`；(3) 每城市设不同颜色 `itemStyle.color`；(4) **模板守卫**：`geoCoordMap || {}`，`map || "china"`

---
...

## Key Points
- This is an official ECharts example from `effectScatter-map/main.js`
- Template data format: `[[x, y, z], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
