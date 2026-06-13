# 股市矩阵图 / Matrix Stock Application

**Category:** `'matrix, candlestick'`
**Example dir:** `matrix-stock`

## Template
⚠️ No template — use knowledge base
Data format: `N/A`

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
    price = lastClose * (1 + (Math.random() - 0.5) * 
```

## Key Points
- Generate via: `scripts/build_template.py  -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
