# 股市矩阵图 / Matrix Stock Application

**Category:** `'matrix, candlestick'`
**Example dir:** `matrix-stock`
**Difficulty:** 3

## Template Match
- **geo/lines.html** — 

## Option Code
```javascript
const lastClose = 50; // Close value of yesterday
const colorGreen = '#47b262';
const colorRed = '#eb5454';
const colorGray = '#888';
const colorGreenOpacity = 'rgba(71, 178, 98, 0.2)';
const colorRedOpacity = 'rgba(235, 84, 84, 0.2)';
const matrixMargin = 10;
const chartWidth = myChart.getWidth();
const chartHeight = myChart.getHeight();
const matrixWidth = chartWidth - matrixMargin * 2;
const matrixHeight = chartHeight - matrixMargin * 2;
const getPriceColor = (price) => {
  return price === lastClose
    ? colorGray
    : price > lastClose
    ? colorRed
    : colorGreen;
};
const priceFormatter = (value) => {
  const result = Math.round(value * 100) / 100 + '';
  // Adding padding 0 if needed
  let dotIndex = result.indexOf('.');
  if (dotIndex < 0) {
    return result + '.00';
  } else if (dotIndex === result.length - 2) {
    return result + '0';
  }
  return result;
};
const priceData = [];
const volumeData = [];
const averageData = []; // Volume weighted average price
const macdData = []; // MACD histogram data
const macdLineData = []; // MACD line (DIF) data
const signalLineData = []; // Signal line (DEA) data
let sumPrice = 0;
let sumVolume = 0;
const sTime = new Date('2025-10-16 09:30:00').getTime();
const eTime = new Date('2025-10-16 15:00:00').getTime();
const breakStartTime = new Date('2025-10-16 11:30:00').getTime();
const breakEndTime = new Date('2025-10-16 13:00:00').getTime();
// MACD algorithm parameters
const shortPeriod = 12; // Short-term EMA period, typically 12
const longPeriod = 26; // Long-term EMA period, typically 26
const signalPeriod = 9; // Signal line EMA period, typically 9
let time = sTime;
let price = 0;
let direction = 1; // 1 for up, -1 for down
let maxAbs = 0;
while (time < eTime) {
  const volume = Math.random() * 1000 + 500;
  volumeData.push([time, volume]);
  sumVolume += volume;
  if (time === sTime) {
    // Today open price
    direction = Math.random() < 0.5 ? 1 : -1;
    price = lastClose * (1 + (Math.random() - 0.5) * 0.02);
  } else {
    // 70% chance to maintain the last direction
    direction = Math.random() < 0.8 ? direction : -direction;
    price = Math.round((price + direction * (Math.random() * 0.1)) * 100) / 100;
  }
  priceData.push([time, price]);
  sumPrice += price * volume;
  averageData.push([time, sumPrice / sumVolume]);
  maxAbs = Math.max(maxAbs, Math.abs(price - lastClose));
  if (time === breakStartTime) {
    time = breakEndTime;
  } else {
    time += 60 * 1000; // increment by 1 minute
  }
}
// Calculate MACD
// 1. Calculate Exponential Moving Average (EMA)
function calculateEMA(prices, period) {
  let ema = [];
  const k = 2 / (period + 1);
  // No special handling for small datasets
  // Just calculate EMA from the period point onwards
  // If we have enough data points
  if (prices.length >= period) {
    // Calculate first EMA using Simple Moving Average (SMA)
    let sum = 0;
    for (let i = 0; i < period; i++) {
      sum += prices[i][1];
    }
    const firstEMA = su
```



## Key Points
- This is an official ECharts example from `matrix-stock/main.js`
- Template data format: `GEO_COORD_MAP + FLIGHTS [[from, to, val], ...]`
- Use `scripts/build_template.py` with the matching template + data
- Always validate with `scripts/validate_chart.py` after generation
