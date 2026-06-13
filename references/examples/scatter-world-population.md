# World Population (2011) / World Population (2011)

**Category:** `scatter`
**Example dir:** `scatter-world-population`

## Template
- **scatter/bubble.html** — Bubble Scatter
Data format: `[[x, y, sizeValue], ...]`

## Option Code
```javascript
var latlong = {};
latlong.AD = { latitude: 42.5, longitude: 1.5 };
latlong.AE = { latitude: 24, longitude: 54 };
latlong.AF = { latitude: 33, longitude: 65 };
latlong.AG = { latitude: 17.05, longitude: -61.8 };
latlong.AI = { latitude: 18.25, longitude: -63.1667 };
latlong.AL = { latitude: 41, longitude: 20 };
latlong.AM = { latitude: 40, longitude: 45 };
latlong.AN = { latitude: 12.25, longitude: -68.75 };
latlong.AO = { latitude: -12.5, longitude: 18.5 };
latlong.AP = { latitude: 35, longitude: 105 };
latlong.AQ = { latitude: -90, longitude: 0 };
latlong.AR = { latitude: -34, longitude: -64 };
latlong.AS = { latitude: -14.3333, longitude: -170 };
latlong.AT = { latitude: 47.3333, longitude: 13.3333 };
latlong.AU = { latitude: -27, longitude: 133 };
latlong.AW = { latitude: 12.5, longitude: -69.9667 };
latlong.AZ = { latitude: 40.5, longitude: 47.5 };
latlong.BA = { latitude: 44, longitude: 18 };
latlong.BB = { latitude: 13.1667, longitude: -59.5333 };
latlong.BD = { latitude: 24, longitude: 90 };
latlong.BE = { latitude: 50.8333, longitude: 4 };
latlong.BF = { latitude: 13, longitude: -2 };
latlong.BG = { latitude: 43, longitude: 25 };
latlong.BH = { latitude: 26, longitude: 50.55 };
latlong.BI = { latitude: -3.5, longitude: 30 };
latlong.BJ = { latitude: 9.5, longitude: 2.25 };
latlong.BM = { latitude: 32.3333, longitude: -64.75 };
latlong.BN = { latitude: 4.5, longitude: 114.6667 };
latlong.BO = { latitude: -17, longitude: -65 };
latlong.BR = { latitude: -10, longitude: -55 };
latlong.BS = { latitude: 24.25, longitude: -76 };
latlong.BT = { latitude: 27.5, longitude: 90.5 };
latlong.BV = { latitude: -54.4333, longitude: 3.4 };
latlong.BW = { latitude: -22, longitude: 24 };
latlong.BY = { latitude: 53, longitude: 28 };
latlong.BZ = { latitude: 17.25, longitude: -88.75 };
latlong.CA = { latitude: 54, longitude: -100 };
latlong.CC = { latitude: -12.5, longitude: 96.8333 };
latlong.CD = { latitude: 0, longitude: 25 };
latlong.CF = { latitude: 7, longitude: 21 };
lat
```

## Key Points
- Generate via: `scripts/build_template.py scatter/bubble.html -d data.json`
- Validate: `scripts/validate_chart.py <output.html>`
