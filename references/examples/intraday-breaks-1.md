# 断轴上的日内走势图 / Intraday Chart with Breaks

**Category:** `candlestick, line`
**Example dir:** `intraday-breaks-1`
**Difficulty:** 4

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
var roundTime = echarts.time.roundTime;
var formatTime = echarts.time.format;
var BREAK_GAP = '1%';
var DATA_ZOOM_MIN_VALUE_SPAN = 3600 * 1000;
var _data = generateData();
option = {
  // Choose axis ticks based on UTC time.
  useUTC: true,
  title: {
    text: 'Intraday Chart with Breaks (Multiple Days)',
    left: 'center'
  },
  tooltip: {
    show: true,
    trigger: 'axis'
  },
  grid: {
    outerBounds: {
      top: '20%',
      bottom: '30%'
    }
  },
  xAxis: [
    {
      type: 'time',
      interval: 1000 * 60 * 30,
      axisLabel: {
        showMinLabel: true,
        showMaxLabel: true,
        formatter(timestamp, _, opt) {
          if (opt.break) {
            // The third parameter is `useUTC: true`.
            return formatTime(timestamp, '{HH}:{mm}\n{weak|{dd}d}', true);
          }
          return formatTime(timestamp, '{HH}:{mm}', true);
        },
        rich: {
          weak: {
            color: '#999'
          }
        }
      },
      breaks: _data.breaks,
      breakArea: {
        expandOnClick: false,
        zigzagAmplitude: 0,
        zigzagZ: 200,
        itemStyle: {
          borderColor: 'none',
          opacity: 0
        }
      }
    }
  ],
  yAxis: {
    type: 'value',
    min: 'dataMin'
  },
  dataZoom: [
    {
      type: 'inside',
      minValueSpan: DATA_ZOOM_MIN_VALUE_SPAN
    },
    {
      type: 'slider',
      top: '73%',
      minValueSpan: DATA_ZOOM_MIN_VALUE_SPAN
    }
  ],
  series: [
    {
      type: 'line',
      symbolSize: 0,
      areaStyle: {},
      data: _data.seriesData
    }
  ]
};

function generateData() {
  var seriesData = [];
  var breaks = [];
  var time = new Date('2024-04-09T00:00:00Z');
  var endTime = new Date('2024-04-12T23:59:59Z').getTime();
  var todayCloseTime = new Date();
  updateDayTime(time, todayCloseTime);
  function updateDayTime(time, todayCloseTime) {
    roundTime(time, 'day', true);
    todayCloseTime.setTime(time.getTime());
    time.setUTCHours(9, 30); // Open time
    todayCloseTime.setUTCHours(16, 0); // Close time
  }
  var valBreak = false;
  for (var val = 1669; time.getTime() <= endTime; ) {
    var delta;
    if (valBreak) {
      delta =
        Math.floor((Math.random() - 0.5 * Math.sin(val / 1000)) * 20 * 100) /
        10;
      valBreak = false;
    } else {
      delta =
        Math.floor((Math.random() - 0.5 * Math.sin(val / 1000)) * 20 * 100) /
        100;
    }
    val = val + delta;
    val = +val.toFixed(2);
    seriesData.push([time.getTime(), val]);
    time.setMinutes(time.getMinutes() + 1);
    if (time.getTime() > todayCloseTime.getTime()) {
      // Use `NaN` to break the line.
      seriesData.push([time.getTime(), NaN]);
      var breakStart = todayCloseTime.getTime();
      time.setUTCDate(time.getUTCDate() + 1);
      updateDayTime(time, todayCloseTime);
      var breakEnd = time.getTime();
      valBreak = true;
      breaks.push({
        start: breakStart,
        end: breakEnd,
        gap: BREAK_GAP
      });
    }

```

## Relevant Debug Patterns
## #14
 — Line XY 数据未排序导致折线锯齿
- **日期**：2026-06-13
- **现象**：08_Line_XY 折线来回穿梭，线条混乱
- **根因**：XY 折线图数据 `[[x,y],...]` 中 x 值未排序。ECharts line chart 按数组顺序连接点，不按 x 值排序
- **修复**：(1) 数据按 x 排序；(2) **模板 `line/xy.html` 新增 `data.sort()` 自动排序**，确保无论输入数据是否有序都能正确渲染

---
...

## #16
 — Stacked bar/line 模板 series 缺少 type 字段
- **日期**：2026-06-13
- **现象**：03_Bar_Stacked、07_Line_Stacked 无数据
- **根因**：`bar/stack.html` 和 `line/stack.html` 使用 `{{SERIES}}` 替换整个 series 数组，每个 series 对象必须带 `type: "bar"/"line"`。ECharts 没有默认 series type
- **修复**：数据 dict 中 series 对象添加 `"type": "bar"` 或 `"type": "line"`

---
...

## #18
 — Scatter Geo/Map 空白：MAP_INLINE 被替换导致地图未加载
- **日期**：2026-06-13
- **现象**：12_Scatter_Geo、13_Map_China 等地图类图表空白
- **根因**：数据 dict 中 `"MAP_INLINE": ""` → `_json_safe` 替换 `{{MAP_INLINE}}` 为 `''` → `<!-- {{MAP_INLINE}} -->` 变成 `<!-- '' -->` → `build_template.py` 的地图注入检测 `if "<!-- {{MAP_INLINE}} -->" in html` 失败 → China GeoJSON 未嵌入 → 地图空白
- **修复**：**不要在数据 dict 中提供 `MAP_INLINE`/`GL_INLINE`/`ECHARTS_INLINE` 这三个特殊占位符**。它们由 `build_template.py` 自动处理（代码中已排除此三类占位符的校验）。**模板不需要修改**——模板中的 `<!-- {{MAP_INLINE}} --...

## Key Points
- This is an official ECharts example from `intraday-breaks-1/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
