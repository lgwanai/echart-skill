# 断轴上的日内走势图 (II) / Intraday Chart with Breaks (II)

**Category:** `candlestick, line`
**Example dir:** `intraday-breaks-2`
**Difficulty:** 4

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
var formatTime = echarts.time.format;
var _data = generateData1();
option = {
  // Choose axis ticks based on UTC time.
  useUTC: true,
  title: {
    text: 'Intraday Chart with Breaks (Single Day)',
    left: 'center'
  },
  tooltip: {
    show: true,
    trigger: 'axis'
  },
  xAxis: [
    {
      type: 'time',
      interval: 1000 * 60 * 30,
      axisLabel: {
        showMinLabel: true,
        showMaxLabel: true,
        formatter: (value, index, extra) => {
          if (!extra || !extra.break) {
            // The third parameter is `useUTC: true`.
            return formatTime(value, '{HH}:{mm}', true);
          }
          // Only render the label on break start, but not on break end.
          if (extra.break.type === 'start') {
            return (
              formatTime(extra.break.start, '{HH}:{mm}', true) +
              '/' +
              formatTime(extra.break.end, '{HH}:{mm}', true)
            );
          }
          return '';
        }
      },
      breakLabelLayout: {
        // Disable auto move of break labels if overlapping,
        // and use `axisLabel.formatter` to control the label display.
        moveOverlap: false
      },
      breaks: [
        {
          start: _data.breakStart,
          end: _data.breakEnd,
          gap: 0
        }
      ],
      breakArea: {
        expandOnClick: false,
        zigzagAmplitude: 0,
        zigzagZ: 200
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
      xAxisIndex: 0
    },
    {
      type: 'slider',
      xAxisIndex: 0
    }
  ],
  series: [
    {
      type: 'line',
      symbolSize: 0,
      data: _data.seriesData
    }
  ]
};

function generateData1() {
  var seriesData = [];
  var time = new Date('2024-04-09T09:30:00Z');
  var endTime = new Date('2024-04-09T15:00:00Z').getTime();
  var breakStart = new Date('2024-04-09T11:30:00Z').getTime();
  var breakEnd = new Date('2024-04-09T13:00:00Z').getTime();
  for (var val = 1669; time.getTime() <= endTime; ) {
    if (time.getTime() <= breakStart || time.getTime() >= breakEnd) {
      val =
        val +
        Math.floor((Math.random() - 0.5 * Math.sin(val / 1000)) * 20 * 100) /
          100;
      val = +val.toFixed(2);
      seriesData.push([time.getTime(), val]);
    }
    time.setMinutes(time.getMinutes() + 1);
  }
  return {
    seriesData: seriesData,
    breakStart: breakStart,
    breakEnd: breakEnd
  };
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
- This is an official ECharts example from `intraday-breaks-2/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
