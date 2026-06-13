# 森林的增长 / Expansion of forest

**Category:** `pictorialBar`
**Example dir:** `pictorialBar-forest`
**Difficulty:** 

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
const treeDataURI =
  'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAA2CAYAAADUOvnEAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA5tJREFUeNrcWE1oE0EUnp0kbWyUpCiNYEpCFSpIMdpLRTD15s2ePHixnj00N4/GoyfTg2fbiwdvvagHC1UQ66GQUIQKKgn1UAqSSFua38b3prPJZDs7s5ufKn0w7CaZ2W/fe9/73kyMRqNB3Nrj1zdn4RJ6du9T2u1a2iHYSxjP4d41oOHGQwAIwSUHIyh8/RA8XeiXh0kLGFoaXiTecw/hoTG4ZCSAaFkY0+BpsZceLtiAoV2FkepZSDk5EpppczBvpuuQCqx0YnkYcVVoqQYMyeCG+lFdaGkXeVOFNu4aEBalOBk6sbQrQF7gSdK5JXjuHXuYVIVyr0TZ0FjKDeCs6km7JYMUdrWAUVmZUBtmRnVPK+x6nIR2xomH06R35ggwJPeofWphr/W5UjPIxq8B2bKgE8C4HVHWvg+2gZjXj19PkdFztY7bk9TDCH/g6oafDPpaoMvZIRI5WyMB/0Hv++HkpTKE0kM+A+h20cPAfN4GuRyp9G+LMTW+z8rCLI8b46XO9zRcYZTde/j0AZm8WGb3Y2F9KLlE2nqYkjFLJAsDOl/lea0q55mqxXcL7YBc++bsCPMe8mUyU2ZIpnCoblca6TZA/ga2Co8PGg7UGUlEDd0ueptglbrRZLLE7poti6pCaWUo2pu1oaYI1CF9b9cCZPO3F8ikJQ/rPpQT5YETht26ss+uCIL2Y8vHwJGpA96GI5mjOlaKhowUy6BcNcgIhDviTGWCGFaqEuufWz4pgcbCh+w0gEOyOjTlTtYYlIWPYWKEsLDzOs+nhzaO1KEpd+MXpOoTUgKiNyhdy5aSMPNVqxtSsJFgza5EWA4zKtCJ2OGbLn0JSLu8+SL4G86p1Fpr7ABXdGFF/UTD4rfmFYFw4G9VAJ9SM3aF8l3yok4/J6IV9sDVb36ynmtJ2M5+CwxTYBdKNMBaocKGV2nYgkz6r+cHBP30MzAfi4Sy+BebSoPIOi8PW1PpCCvr/KOD4k9Zu0WSH0Y0+SxJ2awp/nlwKtcGyHOJ8vNHtRJzhPlsHr8MogtlVtwUU0tSM1x58upSKbfJnSKUR07GVMKkDNfXpzpv0RTHy3nZMVx5IOWdZIaPabGFvfpwpjnvfmJHXLaEvZUTseu/TeLc+xgAPhEAb/PbjO6PBaOTf6LQRh/dERde23zxLtOXbaKNhfq2L/1fAOPHDUhOpIf5485h7l+GNHHiSYPKE3Myz9sFxoJuAyazvwIMAItferha5LTqAAAAAElFTkSuQmCC';
const beginYear = 2016;
const endYear = 2050;
const lineCount = 10;
// Basic option:
option = {
  color: ['#e54035'],
  xAxis: {
    axisLine: { show: false },
    axisLabel: { show: false },
    axisTick: { show: false },
    splitLine: { show: false },
    name: beginYear + '',
    nameLocation: 'middle',
    nameGap: 40,
    nameTextStyle: {
      color: 'green',
      fontSize: 30,
      fontFamily: 'Arial'
    },
    min: -2800,
    max: 2800
  },
  yAxis: {
    data: makeCategoryData(),
    show: false
  },
  grid: {
    top: 'center',
    height: 280
  },
  series: [
    {
      name: 'all',
      type: 'pictorialBar',
      symbol: 'image://' + treeDataURI,
      symbolSize: [30, 55],
      symbolRepeat: true,
      data: makeSeriesData(beginYear),
      animationEasing: 'elasticOut'
    },
    {
      name: 'all',
      type: 'pictorialBar',
      symbol: 'image://' + treeDataURI,
      symbolSize: [30, 55],
      symbolRepeat: true,
      data: makeSeriesData(beginYear, true),
      animationEasing: 'elasticOut'
    }
  ]
};
// Make fake data.
function makeCategoryData() {
  var categoryData = [];
  for (var i = 0; i < lineCount; i++) {
    categoryData.push(i + 'a');
  }
  return categoryData;
}
function makeSeriesData(year, negative) {
  // make a fake value just for demo.
  const r = (year - beginYear + 1) * 10;
  const seriesData = [];
  for (let i = 0; i < lineCount; i++) {
    let sign = negative ? -1 * (i % 3 ? 0.9 : 1) : 1 * ((i + 1) % 3 ? 0.9 : 1);
    seriesData.push({
      value:
        sign *
        (year <= beginYear
```

## Relevant Debug Patterns
## #24
 — PictorialBar：symbol 必须用真实位图，SVG/矢量路径效果差
- **日期**：2026-06-13
- **现象**：28_PictorialBar 显示纯色方块，无象形效果
- **根因**：(1) `SYMBOL: "rect"` → 普通矩形，不"象形"；(2) SVG 手绘路径质量差；(3) `SYMBOL_BOUNDING: "false"` → 无 bounding，所有值显为单个图标
- **修复**：(1) 下载 Twitter emoji CDN 的 72x72 PNG 光栅图（大象/犀牛/河马/水牛/长颈鹿）；(2) 通过 `data[i].symbol` 为每个数据项设置独立图标 URI；`symbolBoundingData: 1000`，`symbolRepeat: true`；(3) **模板增加防御**：`symbol` 为空时允许 data[i].symbol 覆盖

---
...

## Key Points
- This is an official ECharts example from `pictorialBar-forest/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
